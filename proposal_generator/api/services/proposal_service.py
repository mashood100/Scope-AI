import openai
from django.conf import settings
import logging
import os
import re

logger = logging.getLogger(__name__)


class ProposalService:
    """Service class for generating job proposals using AI"""
    
    def __init__(self):
        # Initialize OpenAI client (assuming OpenAI is being used based on dependencies)
        openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self):
        """Load the prompt template from external file"""
        try:
            prompt_file_path = os.path.join(os.path.dirname(__file__), 'proposal_prompt.txt')
            with open(prompt_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error loading prompt template: {str(e)}")
            # Fallback to default prompt
            return self._get_fallback_prompt()
    
    def _get_fallback_prompt(self):
        """Fallback prompt if file loading fails"""
        return """You are a professional freelancer creating a proposal for an Upwork gig. Write a straightforward and to-the-point bid proposal in 150 words. Be technical but informal and ask a question at the end."""
    
    def _extract_role_from_job_description(self, job_description):
        """Extract the role/position from job description"""
        try:
            # Common patterns for role extraction
            patterns = [
                r'looking for (?:a |an )?([^.,\n]+?)(?:to|who|with)',
                r'need (?:a |an )?([^.,\n]+?)(?:to|who|with)',
                r'seeking (?:a |an )?([^.,\n]+?)(?:to|who|with)',
                r'hiring (?:a |an )?([^.,\n]+?)(?:to|who|with)',
                r'require (?:a |an )?([^.,\n]+?)(?:to|who|with)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, job_description.lower())
                if match:
                    role = match.group(1).strip()
                    # Clean up the role
                    role = re.sub(r'\s+', ' ', role)
                    if len(role) > 50:  # If too long, take first part
                        role = role[:50].strip()
                    return role
            
            # Fallback: try to find developer/designer/etc patterns
            fallback_patterns = [
                r'(developer|programmer|designer|freelancer|consultant|expert|specialist)',
                r'(react|vue|angular|python|django|flutter|mobile|web|frontend|backend|fullstack) (developer|engineer)'
            ]
            
            for pattern in fallback_patterns:
                match = re.search(pattern, job_description.lower())
                if match:
                    return match.group(0)
                    
            return "a skilled developer"
            
        except Exception as e:
            logger.error(f"Error extracting role: {str(e)}")
            return "a skilled developer"
    
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
            system_prompt = """You are a professional freelancer creating Writing a straightforward and to-the-point bid proposal to this UpWork gig pasted in 150 words as a freelancer and discuss every aspect of this job technically as a freelancer in informal language. Ask a question about the project in the end. following this exact format and style:

REQUIRED FORMAT:
1. Start with "𝐇𝐢 𝐭𝐡𝐞𝐫𝐞," (use bold Unicode characters)
2. Brief introduction addressing the client's needs directly
3. Section titled "𝐇𝐞𝐫𝐞'𝐬 𝐡𝐨𝐰 𝐈'𝐝 𝐭𝐚𝐜𝐤𝐥𝐞 𝐢𝐭:" followed by 3-4 bullet points
4. End with a technical question about the project dont need any heading just question
5. Portfolio section titled "𝐏𝐨𝐫𝐭𝐟𝐨𝐥𝐢𝐨:" with relevant links
6. Professional closing: "𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬,\n𝐌𝐚𝐬𝐡 𝐇\n𝐓𝐨𝐩 𝐑𝐚𝐭𝐞𝐝 𝐅𝐫𝐞𝐞𝐥𝐚𝐧𝐜𝐞𝐫"
7. Avoid words like Seamless, Robust,  Eager, However
8. Avoid using —

STYLE REQUIREMENTS:
- Use bold Unicode characters for section headers (NOT markdown ** formatting)
- Keep it around 150 words
- Be technical but informal
- Show confidence and expertise
- Include specific technical approach
- Use dashes (-) for portfolio items
- NEVER use markdown formatting like ** or __ — only use bold Unicode characters

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
- Use dashes (-) for portfolio items
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
                    portfolio_urls += f"- {project['name']}"
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
    
    def generate_custom_proposal(self, job_description: str, client_name: str = "", selected_projects: list = None, external_links: dict = None) -> str:
        """
        Generate a job proposal with custom client name, selected projects, and external links
        
        Args:
            job_description: The job description to create a proposal for
            client_name: Client's name for personalized greeting
            selected_projects: List of manually selected portfolio projects
            external_links: Dict with boolean flags for external links (github, stackoverflow, website)
            
        Returns:
            Generated proposal text with custom configuration
        """
        try:
            selected_projects = selected_projects or []
            external_links = external_links or {}
            
            # Build greeting based on client name (make client name bold)
            if client_name.strip():
                # Convert client name to bold Unicode if not already
                bold_client_name = self._make_text_bold(client_name)
                greeting = f"𝐇𝐢 {bold_client_name},"
            else:
                greeting = "𝐇𝐢 𝐭𝐡𝐞𝐫𝐞,"
            
            # Build portfolio context from selected projects
            portfolio_context = ""
            if selected_projects:
                portfolio_context = "\n\nSELECTED PORTFOLIO PROJECTS:\n"
                for project in selected_projects:
                    portfolio_context += f"- {project['name']}: {project.get('ai_summary', project.get('description', ''))[:100]}...\n"
                    if project.get('github_url'):
                        portfolio_context += f"  GitHub: {project['github_url']}\n"
                    if project.get('live_url'):
                        portfolio_context += f"  Live: {project['live_url']}\n"
                    if project.get('app_store_url'):
                        portfolio_context += f"  App Store: {project['app_store_url']}\n"
            
            # Build external links section
            external_portfolio_links = []
            if external_links.get('github'):
                external_portfolio_links.append("- GitHub: https://github.com/mashood100")
            if external_links.get('stackoverflow'):
                external_portfolio_links.append("- Stack Overflow: https://stackoverflow.com/users/12777999/mashood-h")
            if external_links.get('website'):
                external_portfolio_links.append("- Portfolio Website: [Your Personal Website]")
            
            # Extract role from job description
            role = self._extract_role_from_job_description(job_description)
            
            # Build the relevant project mention for the prompt
            relevant_project_mention = ""
            if selected_projects:
                relevant_project_mention = f"Mention the most relevant selected project briefly: {selected_projects[0]['name']}"
            
            # Build the system prompt from the template
            # Replace client name placeholder in template
            if client_name.strip():
                system_prompt = self.prompt_template.replace(
                    "if client name provided: \"𝐇𝐢 {client_name},\" otherwise: \"𝐇𝐢 𝐭𝐡𝐞𝐫𝐞,\"",
                    f"\"𝐇𝐢 {bold_client_name},\""
                )
            else:
                system_prompt = self.prompt_template.replace(
                    "if client name provided: \"𝐇𝐢 {client_name},\" otherwise: \"𝐇𝐢 𝐭𝐡𝐞𝐫𝐞,\"",
                    "\"𝐇𝐢 𝐭𝐡𝐞𝐫𝐞,\""
                )
            
            # Replace other placeholders
            system_prompt = system_prompt.replace("{Client's problem}", role)
            
            # Add context information to the prompt
            if selected_projects:
                system_prompt += f"\n\nSelected Projects Context:\n{portfolio_context}"
            if external_portfolio_links:
                system_prompt += f"\n\nExternal Links to Include:\n" + "\n".join(external_portfolio_links)
            
            user_message = f"Job Description:\n{job_description}"
            
            # Using the newer OpenAI API format
            from openai import OpenAI
            client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=700,
                temperature=0.7,
            )
            
            generated_proposal = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting (** **) that the AI might have added
            generated_proposal = self._clean_markdown_formatting(generated_proposal)
            
            # Post-process to ensure portfolio URLs are included at the bottom
            if selected_projects or external_portfolio_links:
                portfolio_urls = "\n\n𝐀𝐝𝐝𝐢𝐭𝐢𝐨𝐧𝐚𝐥 𝐑𝐞𝐥𝐞𝐯𝐚𝐧𝐭 𝐖𝐨𝐫𝐤:\n"
                
                # Add selected projects
                if selected_projects:
                    for project in selected_projects:
                        portfolio_urls += f"- {project['name']}"
                        if project.get('github_url'):
                            portfolio_urls += f": {project['github_url']}"
                        elif project.get('live_url'):
                            portfolio_urls += f": {project['live_url']}"
                        elif project.get('app_store_url'):
                            portfolio_urls += f": {project['app_store_url']}"
                        portfolio_urls += "\n"
                
                # Add external links
                if external_portfolio_links:
                    for link in external_portfolio_links:
                        portfolio_urls += link + "\n"
                
                # Add portfolio URLs before the closing signature
                if "𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬" in generated_proposal:
                    generated_proposal = generated_proposal.replace(
                        "𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬",
                        portfolio_urls + "\n𝐁𝐞𝐬𝐭 𝐑𝐞𝐠𝐚𝐫𝐝𝐬"
                    )
                else:
                    generated_proposal += portfolio_urls
            
            logger.info(f"Successfully generated custom proposal with {len(selected_projects)} projects and external links: {external_links}")
            return generated_proposal
            
        except Exception as e:
            logger.error(f"Error generating custom proposal: {str(e)}")
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
    
    def _make_text_bold(self, text: str) -> str:
        """
        Convert regular text to bold Unicode characters
        
        Args:
            text: Regular text to convert
            
        Returns:
            Text converted to bold Unicode characters
        """
        # Dictionary mapping regular characters to bold Unicode equivalents
        bold_map = {
            'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉',
            'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓',
            'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
            'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
            'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
            'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
            '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
        }
        
        # Convert each character
        bold_text = ''
        for char in text:
            bold_text += bold_map.get(char, char)
        
        return bold_text
    
