SELECT
 debtor.`id` AS 'S.NO',
 followup.`date` AS 'DATE',
 debtor.`name` AS 'DEBTOR',
 debtor.`account`AS 'ACCOUNT NUMBER',
 debtor.`card_no` AS 'CARD NO.',
 followup.`status_code` AS 'STATUS',
 followup.`remark` AS 'REMARK',
 followup.`remark_by` AS 'REMARK BY',
 debtor.`client_name` AS 'CLIENT',
 debtor.`product_type` AS 'PRODUCT TYPE',
 debtor_followup.`ptp_amount` AS 'PTP AMOUNT',
 debtor.`next_call` AS 'NEXT CALL',
 debtor_followup.`next_call` AS 'NEXT CALL',
 debtor_followup.`ptp_date` AS 'PTP DATE',
 debtor_followup.`claim_paid_amount` AS 'CLAIM PAID AMOUNT',
 debtor_followup.`claim_paid_date` AS 'CLAIM PAID DATE',
 followup.`contact_number` AS 'DIALED NUMBER',
 debtor.`balance` AS 'BALANCE',
 followup.`call_duration` AS 'CALL DURATION'
 
FROM debtor
JOIN debtor_followup
 ON debtor_followup.`debtor_id` = debtor.`id`
JOIN followup
 ON followup.`id` = debtor_followup.`followup_id`
WHERE debtor.`client_id` = 74
AND debtor.`is_aborted` = 0
AND debtor.`is_locked` = 0
AND DATE(followup.datetime) = CURDATE() - INTERVAL 1 DAY