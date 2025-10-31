SELECT
item.id, item.name, item.description, item.quantity, item.unit,
(
	SELECT COUNT(*) > 1 FROM item_revision WHERE item_revision.id = item.id
) as item_has_revisions,
item_tag.id as tag_id, item_tag.name as tag_name,
item_comment.id AS comment_id, item_comment.user_id AS comment_user_id, item_comment.text AS comment_text,
(
	SELECT COUNT(*) > 1 FROM item_comment_revision WHERE item_comment_revision.id = comment_id
) as item_comment_has_revisions
FROM item
LEFT JOIN item_tag_junction ON item_tag_junction.item_id = item.id
LEFT JOIN item_tag ON item_tag.id = item_tag_junction.item_tag_id
LEFT JOIN item_comment ON item_comment.item_id = item.id
WHERE item.is_deleted = False
ORDER BY item.id, item_tag.id, item_comment.id;
