from models.models import mongo, blog_posts,BlogPost
import logging

def update_response_count(title, question_id, selected_answer):
    try:
        # Fetch the entire blog post
        blog_post = mongo.db.blog_posts.find_one({"title": title})
        print(f"Blog post: {blog_post}")
        if not blog_post:
            logging.warning(f"Blog post with title {title} not found.")
            return {'status': 'failure', 'message': 'Blog post not found'}
        
        # Locate the question with the given question_id
        question = next((q for q in blog_post['questions'] if q['question_id'] == question_id), None)
        logging.info(f"Question: {question}")
        logging.info(f"Question_id: {question_id}")
        if not question:
            logging.warning(f"Question with question_id {question_id} not found.")
            return {'status': 'failure', 'message': 'Question not found'}
        
        # Increment the response_count for the selected_answer
        if selected_answer in question['response_count']:
            question['response_count'][selected_answer] += 1
        else:
            logging.warning(f"Selected answer {selected_answer} not valid.")
            return {'status': 'failure', 'message': 'Invalid selected answer'}

        # Update the entire blog post document
        update_result = mongo.db.blog_posts.replace_one({"title": title}, blog_post)

        logging.info(f"Update result: {update_result}")
        if update_result.matched_count == 1:
            logging.info(f"Successfully incremented response count for title {title}, question_id {question_id}, selected_answer {selected_answer}")
            return {'status': 'success'}
        else:
            logging.warning(f"No documents were updated. Verify the title {title}, question_id {question_id}, and selected_answer {selected_answer} exist.")
            return {'status': 'failure', 'message': 'No document was updated'}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {'status': 'failure', 'message': str(e)}
