import logging
import markdown

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

from config import WP_ENDPOINT, WP_USER, WP_APP_PASSWORD, WP_AI_CATEGORY_ID

logger = logging.getLogger(__name__)


def post_report_to_blog(title: str, markdown_content: str) -> tuple[bool, str]:
    if not all([WP_ENDPOINT, WP_USER, WP_APP_PASSWORD]):
        logger.warning("WordPress 설정이 불완전합니다. 블로그 포스팅을 건너뜁니다.")
        return False, "WordPress 설정 누락"

    try:
        html_content = markdown.markdown(markdown_content, extensions=["tables", "fenced_code"])

        wp = Client(WP_ENDPOINT, WP_USER, WP_APP_PASSWORD)

        post = WordPressPost()
        post.title = title
        post.content = html_content
        post.post_status = "publish"

        if WP_AI_CATEGORY_ID and WP_AI_CATEGORY_ID.isdigit():
            post.terms_names = {"category": [int(WP_AI_CATEGORY_ID)]}

        post_id = wp.call(NewPost(post))

        if post_id:
            logger.info("블로그 포스팅 성공: %s (ID: %s)", title, post_id)
            return True, str(post_id)
        else:
            logger.error("블로그 포스팅 실패: 포스트 ID를 받지 못했습니다")
            return False, "포스트 ID를 받지 못함"

    except Exception as e:
        logger.error("블로그 포스팅 오류: %s", e)
        return False, str(e)
