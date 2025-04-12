from flask import jsonify
from flask_openapi3 import APIBlueprint, Tag
from src.api.schema import ArticleDetailQuery, SearchQuery
from src.api.serialization import ArticleDetailSchema, ArticleSchema
from src.db.main import get_async_db_session
from src.log_utils import _logger
from src.service import article_service

explorer_bp = APIBlueprint("explorer", __name__, url_prefix="/explorer")
explorer_tag = Tag(name="Explorer", description=" ")


@explorer_bp.get(
    "/list-articles",
    tags=[explorer_tag],
    responses={
        200: {"description": "List of articles returned successfully"},
        500: {"description": "Internal server error while fetching articles"},
    },
)
async def list_all_articles():
    """
    Returns a list of all articles with basic information.
    """
    try:
        async with get_async_db_session() as session:
            articles = await article_service.retrieve_all_articles(session)

            # Serializer
            schema = ArticleSchema(many=True)
            return (
                jsonify(
                    {
                        "status": "success",
                        "count": len(articles),
                        "data": schema.dump(articles),
                    }
                ),
                200,
            )
    except Exception as e:
        _logger.warning(f"Failed to list articles. error: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while fetching articles.",
        }, 500


@explorer_bp.get(
    "/article-detail",
    tags=[explorer_tag],
    responses={
        200: {"description": "The article detail matching the article_detail_id"},
        404: {"description": "Article detail not found"},
        500: {"description": "Internal server error while fetching the article detail"},
    },
)
async def get_article_detail(query: ArticleDetailQuery):
    """
    Fetches a specific article detail by its ID.

    This endpoint retrieves a single `ArticleDetail` record based on
    the provided `article_detail_id` in the query parameters
    """
    article_detail_id = query.id
    try:
        async with get_async_db_session() as session:
            article_detail = await article_service.retrieve_article_by_id(
                session, article_detail_id
            )

            if not article_detail:
                return (
                    jsonify(
                        {"status": "success", "message": "Article detail not found"}
                    ),
                    404,
                )

            # Serializer
            schema = ArticleDetailSchema()
            return (
                jsonify(
                    {
                        "status": "success",
                        "data": schema.dump(article_detail),
                    }
                ),
                200,
            )
    except Exception as e:
        _logger.warning(
            f"Failed to fetch article detail ID: {article_detail_id}. error: {e}"
        )
        return {
            "status": "error",
            "message": "An internal error occurred while fetching the article detail.",
        }, 500


@explorer_bp.get(
    "/search-articles",
    tags=[explorer_tag],
    responses={
        200: {"description": "Search completed successfully"},
        500: {"description": "Internal server error while searching articles"},
    },
)
async def articles_search(query: SearchQuery):
    """
    Search for article details that match the given keyword in any relevant field.
    Only the most recent version of an article is returned.
    """
    keyword = query.keyword
    try:
        async with get_async_db_session() as session:
            articles_details = await article_service.search_articles_by_keyword(
                session, keyword
            )

            # Serializer
            schema = ArticleDetailSchema(many=True)
            return (
                jsonify(
                    {
                        "status": "success",
                        "count": len(articles_details),
                        "data": schema.dump(articles_details),
                    }
                ),
                200,
            )
    except Exception as e:
        _logger.warning(
            f"Failed to search articles with keyword: {keyword}. error: {e}"
        )
        return {
            "status": "error",
            "message": "An internal error occurred while searching articles.",
        }, 500
