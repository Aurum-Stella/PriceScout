FETCH_INSTRUCTIONS_ = ("""
select id, url, child_attribute, type, parent_id from datalake.scrap_instructions where type = %s  and id>1893
"""
)

INSERT_INSTRUCTION_ =("""
INSERT INTO datalake.scrap_instructions
(id, url, child_attribute, type, parent_id)
VALUES (DEFAULT,  %s, %s, %s, %s)

""")

INSERT_HTML_ = ("""
INSERT INTO datalake.html_content
(instruction_id, created_at, html, shop_name, categories, page)
VALUES (%s, DEFAULT, %s, %s, %s, %s)
""")



FETCH_INSTRUCTIONS = ("""
select id, url, child_attribute, type, parent_id from datalake.scrap_instructions where type = $1  and id>1893
"""
)

INSERT_INSTRUCTION =("""
INSERT INTO datalake.scrap_instructions
(id, url, child_attribute, type, parent_id)
VALUES (DEFAULT,  $1, $2, $3, $4)

""")

INSERT_HTML = ("""
INSERT INTO datalake.html_content
(instruction_id, created_at, html, shop_name, categories, page)
VALUES ($1, DEFAULT, $2, $3, $4, $5)
""")