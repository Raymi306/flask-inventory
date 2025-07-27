SELECT item_comment.id, user_id, text
FROM item_comment 
JOIN item ON item_comment.item_id = item.id
WHERE item.id = %s;
