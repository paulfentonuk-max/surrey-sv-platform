from django.core.management.base import BaseCommand
from sv_platform.apps.impact.models import FinancialProxy

class Command(BaseCommand):
    help = 'Import Surrey County Council Social Value Engine proxies'

    def handle(self, *args, **options):
        proxies = [
            # HEALTH & WELLBEING
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of participation in sports for inactive adults',
                'description': 'Most relevant for projects seeking to increase active adults',
                'financial_value_gbp': 1500.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of participation in sports for inactive young people',
                'description': 'Most relevant for projects seeking to increase active young people',
                'financial_value_gbp': 1500.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of moving an individual from unemployment to employment',
                'description': 'Most relevant for projects seeking to support people into employment',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an unemployed person moving into employment with support',
                'description': 'Most relevant for projects seeking to support people into employment',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an unemployed person moving into employment without support',
                'description': 'Most relevant for projects seeking to support people into employment',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from long-term health condition to full health',
                'description': 'Most relevant for projects seeking to support people with health conditions',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from long-term health condition to full health with support',
                'description': 'Most relevant for projects seeking to support people with health conditions',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from long-term health condition to full health without support',
                'description': 'Most relevant for projects seeking to support people with health conditions',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from poor mental health to full health',
                'description': 'Most relevant for projects seeking to support people with mental health conditions',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from poor mental health to full health with support',
                'description': 'Most relevant for projects seeking to support people with mental health conditions',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from poor mental health to full health without support',
                'description': 'Most relevant for projects seeking to support people with mental health conditions',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from homelessness to a stable home',
                'description': 'Most relevant for projects seeking to support people who are homeless',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from homelessness to a stable home with support',
                'description': 'Most relevant for projects seeking to support people who are homeless',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from homelessness to a stable home without support',
                'description': 'Most relevant for projects seeking to support people who are homeless',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from debt to financial stability',
                'description': 'Most relevant for projects seeking to support people in debt',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from debt to financial stability with support',
                'description': 'Most relevant for projects seeking to support people in debt',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from debt to financial stability without support',
                'description': 'Most relevant for projects seeking to support people in debt',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from social isolation to social inclusion',
                'description': 'Most relevant for projects seeking to support people who are socially isolated',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from social isolation to social inclusion with support',
                'description': 'Most relevant for projects seeking to support people who are socially isolated',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
            {
                'category': 'HEALTH',
                'outcome_name': 'Value of an individual moving from social isolation to social inclusion without support',
                'description': 'Most relevant for projects seeking to support people who are socially isolated',
                'financial_value_gbp': 18000.00,
                'value_basis': 'Social Value Engine - Global proxy, HACT methodology',
                'surrey_hwb_alignment': True,
                'nhs_business_recommendation': True,
            },
        ]

        created_count = 0
        updated_count = 0

        for proxy_data in proxies:
            proxy, created = FinancialProxy.objects.update_or_create(
                outcome_name=proxy_data['outcome_name'],
                defaults=proxy_data
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully imported {created_count} new proxies and updated {updated_count} existing proxies'
        ))
