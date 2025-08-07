import openai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ProposalService:
    """Service class for generating job proposals using AI"""
    
    def __init__(self):
        # Initialize OpenAI client (assuming OpenAI is being used based on dependencies)
        openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
    
    def generate_proposal(self, job_description: str) -> str:
        """
        Generate a job proposal based on the job description
        
        Args:
            job_description: The job description to create a proposal for
            
        Returns:
            Generated proposal text
        """
        try:
            # Enhanced prompt to match the specific format and style
            system_prompt = """You are a professional freelancer creating a proposal for an Upwork gig. Generate a proposal following this exact format and style:

REQUIRED FORMAT:
1. Start with "𝐇𝐢 𝐭𝐡𝐞𝐫𝐞," (use bold Unicode characters)
2. Brief introduction addressing the client's needs directly
3. Section titled "𝐇𝐞𝐫𝐞'𝐬 𝐡𝐨𝐰 𝐈'𝐝 𝐭𝐚𝐜𝐤𝐥𝐞 𝐢𝐭:" followed by 3-4 bullet points
4. End with a technical question about the project
5. Portfolio section titled "𝐏𝐨𝐫𝐭𝐟𝐨𝐥𝐢𝐨:" with relevant links
6. Professional closing: "𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬,\n𝐌𝐚𝐬𝐡 𝐇\n𝐓𝐨𝐩 𝐑𝐚𝐭𝐞𝐝 𝐅𝐫𝐞𝐞𝐥𝐚𝐧𝐜𝐞𝐫"

STYLE REQUIREMENTS:
- Use bold Unicode characters for section headers (NOT markdown ** formatting)
- Keep it around 150 words
- Be technical but informal
- Show confidence and expertise
- Include specific technical approach
- Use checkmarks (✔) for portfolio items
- NEVER use markdown formatting like ** or __ - only use bold Unicode characters

PORTFOLIO LINKS TO USE:
- Android: https://play.google.com/store/apps/details?id=com.blink.burgerlab
- iOS: https://apps.apple.com/us/app/burger-lab/id1555639986
- GitHub: https://github.com/mashood100

Write the proposal as if you're Mash H, a top-rated freelancer with expertise in the technology stack mentioned in the job description."""
            
            user_message = f"Job Description:\n{job_description}"
            
            # Using the newer OpenAI API format
            from openai import OpenAI
            client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if available
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=600,  # Increased to accommodate the formatted structure
                temperature=0.7,  # Balanced creativity and consistency
            )
            
            generated_proposal = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting (** **) that the AI might have added
            generated_proposal = self._clean_markdown_formatting(generated_proposal)
            
            logger.info(f"Successfully generated proposal for job description (length: {len(job_description)})")
            return generated_proposal
            
        except Exception as e:
            logger.error(f"Error generating proposal: {str(e)}")
            raise Exception(f"Failed to generate proposal: {str(e)}")
    
    def generate_proposal_with_portfolio(self, job_description: str, relevant_projects: list) -> str:
        """
        Generate a job proposal with relevant portfolio projects included
        
        Args:
            job_description: The job description to create a proposal for
            relevant_projects: List of relevant portfolio projects with similarity scores
            
        Returns:
            Generated proposal text with portfolio integration
        """
        try:
            # Build portfolio context from relevant projects
            portfolio_context = ""
            if relevant_projects:
                portfolio_context = "\n\nRELEVANT PORTFOLIO PROJECTS:\n"
                for item in relevant_projects:
                    project = item['project']
                    portfolio_context += f"- {project['name']}: {project.get('ai_summary', project.get('description', ''))[:100]}...\n"
                    if project.get('github_url'):
                        portfolio_context += f"  GitHub: {project['github_url']}\n"
                    if project.get('live_url'):
                        portfolio_context += f"  Live: {project['live_url']}\n"
                    if project.get('app_store_url'):
                        portfolio_context += f"  App Store: {project['app_store_url']}\n"
            
            # Build the relevant project mention for the prompt
            relevant_project_mention = ""
            if relevant_projects:
                relevant_project_mention = f"Mention one relevant project briefly: {relevant_projects[0]['project']['name']}"
            
            # Build portfolio integration text
            portfolio_integration = ""
            if relevant_projects:
                portfolio_integration = f"- Include these specific projects in your portfolio section:\n{portfolio_context}"
            
            # Enhanced prompt that includes portfolio projects
            system_prompt = f"""You are Mash H, a professional freelancer creating a proposal for an Upwork gig. Generate a proposal following this exact format and style:

REQUIRED FORMAT:
1. Start with "𝐇𝐢 𝐭𝐡𝐞𝐫𝐞," (use bold Unicode characters)
2. Brief introduction addressing the client's needs directly
3. {relevant_project_mention if relevant_projects else ""}
4. Section titled "𝐇𝐞𝐫𝐞'𝐬 𝐡𝐨𝐰 𝐈'𝐝 𝐭𝐚𝐜𝐤𝐥𝐞 𝐢𝐭:" followed by 3-4 bullet points
5. End with a technical question about the project
6. Portfolio section titled "𝐏𝐨𝐫𝐭𝐟𝐨𝐥𝐢𝐨:" with relevant links
7. Professional closing: "𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬,\\n𝐌𝐚𝐬𝐡 𝐇\\n𝐓𝐨𝐩 𝐑𝐚𝐭𝐞𝐝 𝐅𝐫𝐞𝐞𝐥𝐚𝐧𝐜𝐞𝐫"

STYLE REQUIREMENTS:
- Use bold Unicode characters for section headers (NOT markdown ** formatting)
- Keep it around 150 words
- Be technical but informal
- Show confidence and expertise
- Include specific technical approach
- Use checkmarks (✔) for portfolio items
- If relevant portfolio projects exist, mention one briefly in the introduction
- NEVER use markdown formatting like ** or __ - only use bold Unicode characters

PORTFOLIO INTEGRATION:
{portfolio_integration if relevant_projects else ""}

DEFAULT PORTFOLIO LINKS (use if no specific projects provided):
- Android: https://play.google.com/store/apps/details?id=com.blink.burgerlab
- iOS: https://apps.apple.com/us/app/burger-lab/id1555639986
- GitHub: https://github.com/mashood100

Write the proposal as Mash H, emphasizing your expertise in the required technology stack."""
            
            user_message = f"Job Description:\n{job_description}"
            
            # Using the newer OpenAI API format
            from openai import OpenAI
            client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if available
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=700,  # Increased to accommodate portfolio integration
                temperature=0.7,  # Balanced creativity and consistency
            )
            
            generated_proposal = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting (** **) that the AI might have added
            generated_proposal = self._clean_markdown_formatting(generated_proposal)
            
            # Post-process to ensure portfolio URLs are included at the bottom
            if relevant_projects:
                portfolio_urls = "\n\n𝐀𝐝𝐝𝐢𝐭𝐢𝐨𝐧𝐚𝐥 𝐑𝐞𝐥𝐞𝐯𝐚𝐧𝐭 𝐖𝐨𝐫𝐤:\n"
                for item in relevant_projects:
                    project = item['project']
                    portfolio_urls += f"✔ {project['name']}"
                    if project.get('github_url'):
                        portfolio_urls += f": {project['github_url']}"
                    elif project.get('live_url'):
                        portfolio_urls += f": {project['live_url']}"
                    elif project.get('app_store_url'):
                        portfolio_urls += f": {project['app_store_url']}"
                    portfolio_urls += "\n"
                
                # Add portfolio URLs before the closing signature
                if "𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬" in generated_proposal:
                    generated_proposal = generated_proposal.replace(
                        "𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬",
                        portfolio_urls + "\n𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬"
                    )
                else:
                    generated_proposal += portfolio_urls
            
            logger.info(f"Successfully generated proposal with {len(relevant_projects)} portfolio projects")
            return generated_proposal
            
        except Exception as e:
            logger.error(f"Error generating proposal with portfolio: {str(e)}")
            # Fallback to regular proposal generation
            return self.generate_proposal(job_description)
    
    def extract_job_metadata(self, job_description: str) -> dict:
        """
        Extract metadata from job description (title, budget, etc.)
        This is a simple implementation - could be enhanced with AI extraction
        """
        metadata = {
            'job_title': None,
            'budget_range': None,
            'project_duration': None
        }
        
        # Simple keyword extraction - could be enhanced with AI
        lines = job_description.split('\n')
        for line in lines[:5]:  # Check first 5 lines for title
            if len(line.strip()) > 10 and len(line.strip()) < 100:
                if not metadata['job_title']:
                    metadata['job_title'] = line.strip()
                    break
        
        # Look for budget indicators
        budget_keywords = ['$', 'budget', 'pay', 'rate', 'price', 'cost']
        for line in lines:
            if any(keyword in line.lower() for keyword in budget_keywords):
                metadata['budget_range'] = line.strip()[:100]
                break
        
        return metadata
    
    def _clean_markdown_formatting(self, text: str) -> str:
        """
        Remove markdown formatting (** **) from the generated proposal text
        
        Args:
            text: The generated proposal text that might contain markdown formatting
            
        Returns:
            Clean text without markdown formatting
        """
        import re
        
        # Remove ** bold ** markdown formatting
        # This pattern matches **text** and replaces it with just text
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Also remove any standalone ** that might be left over
        text = text.replace('**', '')
        
        logger.debug("Cleaned markdown formatting from proposal text")
        return text
    
