import os
from openai import OpenAI

class Analyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found. Analysis will be skipped.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def analyze_video(self, comments, description, hashtags):
        if not self.client:
            return {"summary": "N/A", "sentiment": "N/A", "topic": "N/A", "discussion_points": "N/A"}

        comments_text = "\n".join(comments) if comments else "No comments available."
        hashtags_text = ", ".join(hashtags) if hashtags else "No hashtags."
        
        prompt = f"""
        Analyze this TikTok video based on the following data:
        
        Description: {description}
        Hashtags: {hashtags_text}
        User Comments:
        {comments_text}
        
        Please provide:
        1. Video Topic: What is this video mainly about? (Infer from description/hashtags)
        2. Key Discussion Points: What are the main things people are saying or debating in the comments?
        3. Overall Sentiment: (Positive, Negative, Neutral, Mixed)
        4. Sentiment Score: (1-10, where 10 is extremely positive)
        
        Format the output exactly as follows:
        Topic: [Topic]
        Discussion: [Key points]
        Sentiment: [Sentiment]
        Score: [Score]
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            content = response.choices[0].message.content
            
            # Simple parsing
            result = {}
            for line in content.split('\n'):
                if line.startswith("Topic:"): result['topic'] = line.replace("Topic:", "").strip()
                if line.startswith("Discussion:"): result['discussion'] = line.replace("Discussion:", "").strip()
                if line.startswith("Sentiment:"): result['sentiment'] = line.replace("Sentiment:", "").strip()
                if line.startswith("Score:"): result['score'] = line.replace("Score:", "").strip()
            
            return result
        except Exception as e:
            print(f"Error analyzing video: {e}")
            return {"topic": "Error", "discussion": "Error", "sentiment": "Error", "score": "0"}
