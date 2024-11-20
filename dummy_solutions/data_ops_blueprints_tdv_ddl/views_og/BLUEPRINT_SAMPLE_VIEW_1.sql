--liquibase formatted sql

--changeset Hinds:HSETL_WORKdev.tables.BLUEPRINT_SAMPLE_VIEW_1 runAlways:false runOnChange:true labels:eds,view context:dev,test,prod
--comment: Create view HSETL_WORKdev.BLUEPRINT_SAMPLE_VIEW_1

------------------------------------------------------------------------------------------
CREATE VIEW HSETL_WORKdev.BLUEPRINT_SAMPLE_VIEW_1 AS LOCKING ROW FOR ACCESS SELECT * FROM HSETL_WORKdev.BLUEPRINT_SAMPLE_TABLE_1;

--rollback DROP VIEW HSETL_WORKdev.BLUEPRINT_SAMPLE_VIEW_1;