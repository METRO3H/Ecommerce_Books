
-- Remove all products!

DELETE relations.*, taxes.*, terms.*

FROM wp_term_relationships AS relations

INNER JOIN wp_term_taxonomy AS taxes

ON relations.term_taxonomy_id=taxes.term_taxonomy_id

INNER JOIN wp_terms AS terms

ON taxes.term_id=terms.term_id

WHERE object_id IN (SELECT ID FROM wp_posts WHERE post_type IN ('product','product_variation'));

DELETE FROM wp_postmeta WHERE post_id IN (SELECT ID FROM wp_posts WHERE post_type IN ('product','product_variation'));

DELETE FROM wp_posts WHERE post_type IN ('product','product_variation');