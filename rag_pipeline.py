import os
import json
from typing import List, Dict

class RAGPipeline:
    """Simple keyword-based search for bus provider information (No ML required)"""
    def __init__(self):
        self.documents = []
        self.load_documents()
    
    def load_documents(self):
        """Load bus provider documents from attachment folder"""
        attachment_dir = "attachment"
        provider_files = [
            "desh travel.txt",
            "ena.txt",
            "green line.txt",
            "hanif.txt",
            "shyamoli.txt",
            "soudia.txt"
        ]
        
        for filename in provider_files:
            filepath = os.path.join(attachment_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    provider_name = filename.replace('.txt', '').title()
                    self.documents.append({
                        'provider': provider_name,
                        'content': content,
                        'filename': filename
                    })
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Simple keyword-based search"""
        if not self.documents:
            return []
        
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            # Count keyword matches
            content_lower = doc['content'].lower()
            score = sum(1 for word in query_lower.split() if word in content_lower)
            
            if score > 0:
                results.append({
                    'provider': doc['provider'],
                    'content': doc['content'],
                    'relevance_score': score / len(query_lower.split())  # Normalize score
                })
        
        # Sort by score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:top_k]
    
    def query(self, question: str) -> str:
        """Answer questions about bus providers using keyword search"""
        results = self.search(question)
        
        if not results:
            return "I couldn't find specific information about that. Please try asking about specific bus providers like Hanif, Green Line, Shyamoli, Ena, Soudia, or Desh Travel."
        
        # Build response from top results
        response = f"Based on the information available:\n\n"
        for i, result in enumerate(results[:2], 1):
            response += f"{result['provider']}:\n{result['content'][:300]}...\n\n"
        
        return response
    
    def get_provider_info(self, provider_name: str) -> Dict:
        """Get specific provider information"""
        for doc in self.documents:
            if provider_name.lower() in doc['provider'].lower():
                return doc
        return None
    
    def extract_contact_info(self, content: str) -> Dict:
        """Extract contact information from content"""
        import re
        
        contact_info = {}
        
        # Extract phone numbers
        phone_pattern = r'(?:Phone|Mobile|Contact|Tel)[\s:]*([+\d\s\-()]{10,})'
        phone_match = re.search(phone_pattern, content, re.IGNORECASE)
        if phone_match:
            contact_info['phone'] = phone_match.group(1).strip()
        
        # Extract email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_match = re.search(email_pattern, content)
        if email_match:
            contact_info['email'] = email_match.group(0)
        
        # Extract website
        website_pattern = r'(?:www\.|https?://)[^\s]+'
        website_match = re.search(website_pattern, content)
        if website_match:
            contact_info['website'] = website_match.group(0)
        
        # Extract address
        address_pattern = r'(?:Address|Location)[\s:]*([^\n]{10,100})'
        address_match = re.search(address_pattern, content, re.IGNORECASE)
        if address_match:
            contact_info['address'] = address_match.group(1).strip()
        
        return contact_info

# Global instance
rag_pipeline = RAGPipeline()
