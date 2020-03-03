
-- 在个人预约表中，创建终检完成时间索引
CREATE INDEX idx_personal_order_main_check_date ON t_personal_order (MAIN_CHECK_DATE);

-- 个人基本情况示图

DROP VIEW
IF EXISTS v_lk_baseinfo;

CREATE VIEW v_lk_baseinfo AS SELECT
	-- 体检号
	person.EXAM_NO ,

  -- 合同号
  porder.CONTRACT_ID,

	-- 预约号
	porder.ID AS ORDER_ID,
	-- 报道日期
	porder.ARRIVAL_DATE,
	-- 姓名
	person.USERNAME,
	-- 性别编码
	sex.BASE_CODE AS SEX_CODE,
	-- 性别名称
	sex.BASE_VALUE AS SEX_NAME,
	-- 出生日期
	person.BIRTHDAY,
	-- 年龄
	porder.AGE,
	-- 身份证
	person.CERT_ID,
	-- 手机
	person.TELEPHONE,
	-- 婚姻状况编码
	porder.MARITAL_STATUS,
	-- 婚姻状况名称
	marial.BASE_VALUE AS MARITAL_NAME,
	-- 邮箱
	person.EMAIL,
	-- 工作单位编码
	org.ID ORG_ID,
	-- 工作单位名称
	org.`NAME` ORG_NAME,
	-- 终检完成日期
	porder.MAIN_CHECK_DATE,
	-- 体检状态
	porder.EXAM_STATUS
FROM
	t_personal_order porder
INNER JOIN t_person person ON porder.PERSON_ID = person.ID
LEFT JOIN t_base_dict sex ON person.SEX = sex.BASE_CODE
AND sex.TYPE = '性别'
LEFT JOIN t_base_dict marial ON porder.MARITAL_STATUS = marial.BASE_CODE
AND marial.TYPE = '婚姻状态'
LEFT JOIN t_organization org ON porder.ORGANIZATION_ID = org.ID
WHERE
	porder.EXAM_STATUS IN (
		'报告已打印',
		'报告已交接',
		'报告送达'
	);


-- 费用

DROP VIEW
IF EXISTS v_lk_fare;

CREATE VIEW v_lk_fare AS SELECT
  UUID() as ID,
	ORDER_ID,
	ORIGINAL_AMOUNT ORIGINAL_AMOUNT,
	DISCOUNT_AMOUNT DISCOUNT_AMOUNT,
	UNIT_OR_OWN
FROM
	t_person_element_assem passem
WHERE
	SYMBOL = '有效';



-- 主检疾病、建议
DROP VIEW
IF EXISTS v_lk_recheck;

CREATE VIEW v_lk_recheck AS SELECT
  UUID() as ID,
	recheck.ORDER_ID,
	recheck.RECOMMEND,
	detail.MERGE_WORD,
	porder.MAIN_CHECK_DATE,
	operator.REAL_NAME
FROM
	t_recheck_result recheck
INNER JOIN t_recheck_result_detail detail ON detail.RECHECK_RESULT_ID = recheck.ID
INNER JOIN t_personal_order porder ON recheck.ORDER_ID = porder.ID
LEFT JOIN t_operator operator ON porder.MAIN_CHECK_UID = operator.ID;

-- 检查结果列表
DROP VIEW
IF EXISTS v_lk_results;

CREATE VIEW v_lk_results AS SELECT
	UUID() AS ID,
	summary.ORDER_ID,
	department.id AS DEPARTMENT_ID,
	department.`NAME` AS DEPARTMENT_NAME,
	summary.ELEMENT_ASSEM_ID,
	assem.`NAME` AS ASSEM_NAME,
	operator.REAL_NAME,
	deta.MERGE_WORD,
	assem.DISPLAY_ORDER ASSEM_DISPLAY_ORDER,
	results.ELEMENT_ID,
	element.`NAME` ELEMENT_NAME,
	assemdetail.DISPLAY_ORDER ELEMENT_DISPLAY_ORDER,
	results.OPT_TIME,
	element.DEFAULT_VALUE,
	results.RESULT_CONTENT,
	results.MEASUREMENT_UNIT,
	results.FERENCE_LOWER_LIMIT,
	results.FERENCE_UPPER_LIMIT,
  results.POSITIVE_SYMBOL
FROM
	T_ELEMENT_ASSEM_SUMMARY summary
INNER JOIN t_element_assem_summary_deta deta ON summary.ID = deta.ELEMENTCLASS_SUMMARY_ID
INNER JOIN t_element_assem_sub assem ON summary.ELEMENT_ASSEM_ID = assem.ID
INNER JOIN t_department department ON assem.DEPARTMENT_ID = department.ID
LEFT JOIN t_operator operator ON summary.OPERATOR_ID = operator.ID
INNER JOIN t_element_results results ON summary.ORDER_ID = results.ORDER_ID
AND summary.ELEMENT_ASSEM_ID = results.ELEMENT_ASSEM_ID
INNER JOIN t_element_sub element ON results.ELEMENT_ID = element.ID
INNER JOIN t_element_assem_detail_sub assemdetail ON summary.ELEMENT_ASSEM_ID = assemdetail.ELEMENT_ASSEM_ID
AND element.ID = assemdetail.ELEMENT_ID
WHERE
	summary.CANCEL_SYMBOL = '有效'
AND SAVE_SYMBOL = '提交'
AND deta.SELFWRITE_SYMBOL <> '04'
ORDER BY department.DISPLAY_ORDER,assem.DISPLAY_ORDER, assemdetail.DISPLAY_ORDER;

--- 创建用户
DROP USER
IF EXISTS 'lkhnjk'@'%';

CREATE USER 'lkhnjk'@'%' IDENTIFIED BY 'lkhnjk!QAZ';

grant select on jk.v_lk_baseinfo to 'lkhnjk'@'%' identified by 'lkhnjk!QAZ' with grant option;

grant select on jk.v_lk_fare to 'lkhnjk'@'%' identified by 'lkhnjk!QAZ' with grant option;

grant select on jk.v_lk_recheck to 'lkhnjk'@'%' identified by 'lkhnjk!QAZ' with grant option;

grant select on jk.v_lk_results to 'lkhnjk'@'%' identified by 'lkhnjk!QAZ' with grant option;



