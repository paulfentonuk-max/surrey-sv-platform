import io
import base64
import hashlib
import time
from PIL import Image
from django.core.cache import cache
from django.conf import settings
import json

class AROLOptimizationService:
    """
    AI Request Optimization Layer
    Minimizes data transfer and token usage for Venice AI API calls
    """
    
    def __init__(self):
        self.cache_ttl = 604800
        self.compression_quality = 85
        self.target_image_size = (224, 224)
    
    def optimize_vision_request(self, image_data, prompt, request_id=None):
        start_time = time.time()
        metrics = {
            'original_size': len(image_data),
            'optimizations_applied': [],
        }
        
        # Step 1: Strip metadata
        image_data = self._strip_metadata(image_data)
        metrics['optimizations_applied'].append('metadata_stripping')
        
        # Step 2: Resize to model input dimensions
        image_data = self._resize_for_model(image_data)
        metrics['optimizations_applied'].append('resize')
        
        # Step 3: Convert to WebP
        image_data = self._convert_to_webp(image_data)
        metrics['optimizations_applied'].append('webp_conversion')
        
        # Step 4: Apply compression
        image_data = self._compress_image(image_data)
        metrics['optimizations_applied'].append('compression')
        
        optimized_size = len(image_data)
        reduction_percent = ((metrics['original_size'] - optimized_size) / metrics['original_size']) * 100
        
        preprocessing_time = int((time.time() - start_time) * 1000)
        
        metrics.update({
            'optimized_size': optimized_size,
            'reduction_percent': reduction_percent,
            'preprocessing_time_ms': preprocessing_time,
        })
        
        return image_data, metrics
    
    def optimize_text_request(self, prompt, context=None):
        start_time = time.time()
        metrics = {
            'original_tokens': self._estimate_tokens(prompt),
            'optimizations_applied': [],
        }
        
        # Step 1: Remove redundant whitespace
        prompt = self._normalize_whitespace(prompt)
        metrics['optimizations_applied'].append('whitespace_normalization')
        
        # Step 2: Use structured format
        if context and context.get('structured_output'):
            prompt = self._structure_for_json_mode(prompt)
            metrics['optimizations_applied'].append('json_mode')
        
        # Step 3: Remove unnecessary pleasantries
        prompt = self._remove_social_noise(prompt)
        metrics['optimizations_applied'].append('social_noise_removal')
        
        # Step 4: Add format instructions inline
        if context and context.get('output_format'):
            prompt = self._inline_format_instructions(prompt, context['output_format'])
            metrics['optimizations_applied'].append('inline_formatting')
        
        optimized_tokens = self._estimate_tokens(prompt)
        token_savings = metrics['original_tokens'] - optimized_tokens
        
        preprocessing_time = int((time.time() - start_time) * 1000)
        
        metrics.update({
            'optimized_tokens': optimized_tokens,
            'token_savings': token_savings,
            'savings_percent': (token_savings / metrics['original_tokens']) * 100 if metrics['original_tokens'] > 0 else 0,
            'preprocessing_time_ms': preprocessing_time,
        })
        
        return prompt, metrics
    
    def check_cache(self, request_type, content_hash):
        cache_key = f"arol:{request_type}:{content_hash}"
        cached_result = cache.get(cache_key)
        
        return {
            'hit': cached_result is not None,
            'key': cache_key,
            'result': cached_result,
        }
    
    def cache_result(self, cache_key, result, ttl=None):
        if ttl is None:
            ttl = self.cache_ttl
        
        cache.set(cache_key, result, ttl)
    
    def _strip_metadata(self, image_data):
        img = Image.open(io.BytesIO(image_data))
        data = io.BytesIO()
        
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        img.save(data, format=img.format or 'JPEG')
        return data.getvalue()
    
    def _resize_for_model(self, image_data):
        img = Image.open(io.BytesIO(image_data))
        img = img.resize(self.target_image_size, Image.Resampling.LANCZOS)
        
        data = io.BytesIO()
        img.save(data, format='JPEG', quality=self.compression_quality)
        return data.getvalue()
    
    def _convert_to_webp(self, image_data):
        img = Image.open(io.BytesIO(image_data))
        
        data = io.BytesIO()
        img.save(data, format='WebP', quality=self.compression_quality, method=6)
        return data.getvalue()
    
    def _compress_image(self, image_data):
        if len(image_data) > 500 * 1024:
            img = Image.open(io.BytesIO(image_data))
            data = io.BytesIO()
            img.save(data, format='WebP', quality=70, method=6)
            return data.getvalue()
        return image_data
    
    def _normalize_whitespace(self, text):
        import re
        return re.sub(r'\s+', ' ', text).strip()
    
    def _remove_social_noise(self, text):
        import re
        social_patterns = [
            r'^(Hi|Hello|Hey|Greetings)[,.!]?\s*',
            r'(Please|Kindly|Could you|Would you mind)[,]?\s*',
            r'(Thanks|Thank you|Cheers|Best regards)[,.!]?\s*$',
            r'\s*(I hope this helps|Let me know if you need anything)\.?$',
        ]
        
        for pattern in social_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _structure_for_json_mode(self, prompt):
        if 'return as json' not in prompt.lower():
            prompt += " Return your response as a valid JSON object."
        return prompt
    
    def _inline_format_instructions(self, prompt, format_spec):
        format_str = json.dumps(format_spec, indent=2)
        return f"{prompt}\n\nFormat your response exactly as follows:\n{format_str}"
    
    def _estimate_tokens(self, text):
        return len(text) // 4
    
    def generate_content_hash(self, content):
        if isinstance(content, bytes):
            return hashlib.sha256(content).hexdigest()[:16]
        return hashlib.sha256(content.encode()).hexdigest()[:16]
