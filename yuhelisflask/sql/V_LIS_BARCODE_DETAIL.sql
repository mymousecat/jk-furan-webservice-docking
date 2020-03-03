DROP VIEW
IF EXISTS V_LIS_BARCODE_DETAIL;

CREATE VIEW V_LIS_BARCODE_DETAIL AS SELECT
	a.ID AS BARCODE_ID,
	e.ID AS ELEMENT_ASSEM_ID,
	e.EXTERNAL_SYS_CONTROL_CODE AS LIS_ELEMENT_ASSEM_ID,
  e. NAME AS ELEMENT_ASSEM_NAME,
	element.ID AS ELEMENT_ID,
	element. NAME AS ELEMENT_NAME,
	element.EXTERNAL_SYS_CONTROL_CODE AS LIS_ELEMENT_CODE
FROM
	t_barcode a
JOIN t_personal_order c ON a.ORDER_ID = c.ID
JOIN t_barcode_detail g ON g.BARCODE_ID = a.ID
JOIN t_element_assem_sub e ON g.ELEMENT_ASSEM_ID = e.ID
JOIN t_element_assem_detail_sub sub ON e.ID = sub.ELEMENT_ASSEM_ID
JOIN t_element_sub element ON element.ID = sub.ELEMENT_ID;

GRANT SELECT ON jk.V_LIS_BARCODE_DETAIL TO lis@'%';