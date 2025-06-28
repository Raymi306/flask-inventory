SELECT item_tag.id, item_tag.name
FROM item_tag
JOIN item_tag_junction ON item_tag.id = item_tag_junction.item_tag_id
JOIN item ON item_tag_junction.item_id = item.id
WHERE item.id = %s;
