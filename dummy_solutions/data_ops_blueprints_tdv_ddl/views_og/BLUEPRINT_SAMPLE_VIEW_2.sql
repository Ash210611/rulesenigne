--liquibase formatted sql

--changeset Hinds:HSETL_WORK${dbEnv}.tables.BLUEPRINT_SAMPLE_TABLE_2 runAlways:false runOnChange:true labels:eds,view context:dev,test,prod
--comment: Create view HSETL_WORK${dbEnv}.BLUEPRINT_SAMPLE_TABLE_2

------------------------------------------------------------------------------------------

CREATE VIEW HSETL_WORK${dbEnv}.BLUEPRINT_SAMPLE_VIEW_2 AS LOCKING ROW FOR ACCESS SELECT * FROM HSETL_WORK${dbEnv}.BLUEPRINT_SAMPLE_TABLE_2;

--rollback DROP VIEW HSETL_WORK${dbEnv}.BLUEPRINT_SAMPLE_VIEW_2;