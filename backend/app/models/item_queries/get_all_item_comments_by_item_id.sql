SELECT item_comment.id, user_id, text,
(
	SELECT COUNT(*) > 1 FROM item_comment_revision WHERE item_comment_revision.id = item_comment.id
) as has_revisions
FROM item_comment 
JOIN item ON item_comment.item_id = item.id
WHERE item.id = %s;
