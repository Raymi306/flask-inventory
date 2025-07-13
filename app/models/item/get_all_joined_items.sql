SELECT
item.id, item.name, item.description, item.quantity, item.unit,
item_tag.id as tag_id, item_tag.name as tag_name,
item_comment.id AS comment_id, item_comment.user_id AS comment_user_id, item_comment.text AS comment_text
FROM item
JOIN item_tag_junction ON item_tag_junction.item_id = item.id
LEFT JOIN item_tag ON item_tag.id = item_tag_junction.item_tag_id
LEFT JOIN item_comment ON item_comment.item_id = item.id
ORDER BY item.id, item_tag.id, item_comment.id;
