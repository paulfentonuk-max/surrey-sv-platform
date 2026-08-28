import os
import json
import base64
from typing import List, Dict, Optional
import requests
from django.conf import settings
from sv_platform.apps.arol.services import AROLOptimizationService

class VeniceAIClient:
    def __init__(self):
        self.api_key = settings.VENICE_API_KEY
        self.base_url = settings.VENICE_BASE_URL
        self.arol = AROLOptimizationService()
        
    def _headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def chat_completion(self, messages: List[Dict], model: str = "default", temperature: float = 0.7):
        # AROL optimization for text
        if messages and len(messages) > 0:
            original_content = messages[0].get('content', '')
            optimized_content, metrics = self.arol.optimize_text_request(
                original_content,
                context={'structured_output': True}
            )
            messages[0]['content'] = optimized_content
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
        )
        return response.json()
    
    def vision_analysis(self, image_url: str, prompt: str):
        # Download and optimize image
        import urllib.request
        from PIL import Image
        import io
        
        # Download image
        with urllib.request.urlopen(image_url) as response:
            image_data = response.read()
        
        # AROL optimization
        optimized_image, metrics = self.arol.optimize_vision_request(image_data, prompt)
        
        # Convert to base64 for API
        image_b64 = base64.b64encode(optimized_image).decode('utf-8')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/webp;base64,{image_b64}"}}
                ]
            }
        ]
        return self.chat_completion(messages, model="vision")

class ActivityAnalysisService:
    def __init__(self):
        self.client = VeniceAIClient()
        self.arol = AROLOptimizationService()
    
    def analyze_submission(self, submission):
        if submission.input_type == 'IMAGE':
            return self._analyze_image(submission)
        elif submission.input_type == 'TEXT':
            return self._analyze_text(submission)
        elif submission.input_type == 'VOICE':
            return self._analyze_voice(submission)
        else:
            return self._analyze_mixed(submission)
    
    def _analyze_image(self, submission):
        prompt = """
        Analyze this community activity image. Identify:
        1. What activity is taking place
        2. Who is participating (demographics if visible)
        3. The setting and context
        4. Potential social value outcomes
        5. Health and wellbeing impacts
        6. Community cohesion indicators
        Return structured JSON with these fields.
        """
        
        image_url = submission.media_files[0] if submission.media_files else None
        if image_url:
            result = self.client.vision_analysis(image_url, prompt)
            return self._parse_analysis(result)
        return {}
    
    def _analyze_text(self, submission):
        prompt = f"""
        Analyze this community activity description for social value impact:
        "{submission.text_content}"
        Context: Community in {submission.community_context}
        Provide: Activity classification, Target beneficiary groups, Estimated outcomes and metrics,
        Potential SROI indicators, Alignment with Surrey Health and Wellbeing Strategy, Preventative value assessment.
        Return as structured JSON.
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = self.client.chat_completion(messages)
        return self._parse_analysis(result)
    
    def _analyze_voice(self, submission):
        return self._analyze_text(submission)
    
    def _analyze_mixed(self, submission):
        analyses = []
        if submission.text_content:
            analyses.append(self._analyze_text(submission))
        if submission.media_files:
            analyses.append(self._analyze_image(submission))
        return self._merge_analyses(analyses)
    
    def _parse_analysis(self, ai_response):
        try:
            content = ai_response['choices'][0]['message']['content']
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            return json.loads(content)
        except:
            return {'raw_analysis': content}
    
    def _merge_analyses(self, analyses):
        merged = {}
        for analysis in analyses:
            merged.update(analysis)
        return merged

class ActivityGenerationService:
    def __init__(self):
        self.client = VeniceAIClient()
    
    def generate(self, generation_request):
        communities = generation_request.target_communities.all()
        community_profiles = [
            {
                'id': str(c.id),
                'disadvantage_score': c.composite_disadvantage_score,
                'emerging_needs': c.emerging_needs_flags,
                'health_inequality': c.health_inequality_index
            }
            for c in communities
        ]
        
        prompt = f"""
        Generate optimal community activities for maximum Social Value ROI and preventative impact.
        TARGET COMMUNITIES: {json.dumps(community_profiles)}
        CONSTRAINTS: Budget: £{generation_request.budget_constraint or 'Flexible'}, Priority Groups: {generation_request.priority_groups}, Focus: {generation_request.generation_type}
        Generate 3 activity options with: Activity name and description, Target beneficiaries, Expected outcomes and quantities, Estimated costs, Predicted SROI ratio, Preventative impact score (1-10), Implementation steps, Evaluation metrics.
        Return as JSON array.
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = self.client.chat_completion(messages, temperature=0.8)
        
        try:
            activities = json.loads(result['choices'][0]['message']['content'])
            generation_request.generated_activities = activities
            srois = [a.get('predicted_sroi', 0) for a in activities]
            generation_request.predicted_sroi = max(srois) if srois else None
            generation_request.save()
            return activities
        except Exception as e:
            return {'error': str(e), 'raw': result}

class ProjectGenerationService:
    def __init__(self):
        self.client = VeniceAIClient()
    
    def generate_project(self, activity, user_requirements):
        business_case = self._generate_business_case(activity, user_requirements)
        project_plan = self._generate_project_plan(activity, user_requirements)
        risk_register = self._generate_risk_register(activity)
        
        return {
            'business_case': business_case,
            'project_plan': project_plan,
            'risk_register': risk_register,
        }
    
    def _generate_business_case(self, activity, requirements):
        prompt = f"""
        Create a PRINCE2 Business Case for this community activity:
        ACTIVITY: {activity.selected_activity}
        USER REQUIREMENTS: {json.dumps(requirements)}
        Include: Executive Summary, Reasons, Business Options, Expected Benefits, Major Risks, Timescales, Costs, Investment Appraisal.
        Return as structured JSON.
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = self.client.chat_completion(messages)
        return self._extract_json(result)
    
    def _generate_project_plan(self, activity, requirements):
        prompt = f"""
        Create a detailed Project Plan following PRINCE2 methodology:
        ACTIVITY: {activity.selected_activity}, BUDGET: £{activity.budget_constraint}
        Include: Project Stages and Deliverables, Work Packages, Dependencies, Resource Requirements, Schedule, Quality Criteria, Social Value specific deliverables.
        Return as structured JSON.
        """
        
        messages = [{"role": "user", "content": prompt}]
        result = self.client.chat_completion(messages)
        return self._extract_json(result)
    
    def _generate_risk_register(self, activity):
        prompt = "Generate a Risk Register for community delivery project. Include typical risks: Community engagement, Funding/financial, Delivery partner, Outcome measurement, External factors. For each: ID, Description, Probability, Impact, Mitigation, Owner. Return as JSON array."
        
        messages = [{"role": "user", "content": prompt}]
        result = self.client.chat_completion(messages)
        return self._extract_json(result)
    
    def _extract_json(self, result):
        try:
            content = result['choices'][0]['message']['content']
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            return json.loads(content)
        except:
            return {'content': result['choices'][0]['message']['content']}
