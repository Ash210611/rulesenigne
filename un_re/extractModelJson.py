# pylint: disable=W0311		# Ignore different indentation 
# pylint: disable=C0209		# don't require formatted strings
# pylint: disable=C0200		# Don't require enumerate
#
# ! extractModelJson.py
# ========|=========|=========|=========|=========|=========|=========|=========|====|
#   Beverly King De Loach
#   10/25/2020
#  ----------------------------------------------------------------------------------
#  FUNCTION:
#  1. open the json model file (path and json filename passed in)  ASSUMPTION is that
#      the JSON file follows the structure of the Data Model Classes/Json output from
#      REDD tool
#  2. create sqlite in-memory tables to hold data from JSON file
#  3. populate the table(s)
#
#  ASSUMPTIONS:
#   this calling script should have :
#       import extractModelJson as J
#       import sqlite3
#       _path = 'C:/Temp' <-- example
#       _filename = 'Data Model Validator.Json'  <-- example
#
#       J.extractJson(_path, _filename)
#
#   ex of use for entity/table -- cEntity cursor:
#       J.cEntity.execute("SELECT COUNT(*) from ENTTY ")
#       (KNTR) = J.cEntity.fetchone()[0]
#       J.cEntity.execute("SELECT ENTTY_NM, ENTTY_DEFN_TXT, TBL_NM, TBL_CMMNT_TXT
#               from ENTTY ORDER BY ENTTY_ID")
#       for x in range (0,KNTR):
#           (ENTTY_NM, ENTTY_DEFN_TXT, TBL_NM, TBL_CMMNT_TXT) = J.cEntity.fetchone()
#           if len(ENTTY_DEFN_TXT) > 250:
#           print("BAD Entity Definition!", ENTTY_NM)
#           ...
#
#  AVAILABLE DATA STRUCTURES:
#       Available tables are listed in structure definitions at end of this script
# ========|=========|=========|=========|=========|=========|=========|=========|====|
import json
import sqlite3


# ========|=========|=========|=========|=========|=========|=========|=========|====|
#    FUNCTIONS
# ------------------------------------------------------------------------------------
def clearRecArray(arrayNm):
    for x in range(0, len(arrayNm)):
        arrayNm[x][1] = None


def writeModelRec(modelRec):
    if not modelRec[1][1] is None:  # MODEL_NM
        S1 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            modelRec[0][1], modelRec[1][1], modelRec[2][1], modelRec[3][1],
            modelRec[4][1], modelRec[5][1], modelRec[6][1], modelRec[7][1])
        S2 = '"{0}", "{1}", "{2}", "{3}") '.format(
            modelRec[8][1], modelRec[9][1], modelRec[10][1], modelRec[11][1])
        sql_string = 'INSERT INTO MODEL VALUES(' + S1 + S2
        cModel.execute(sql_string)
        clearRecArray(modelRec)


def writeEntityRec(entityRec):
    if not entityRec[5][1] is None:  # TBL_NM
        S1 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            entityRec[0][1], entityRec[1][1], entityRec[2][1], entityRec[3][1],
            entityRec[4][1], entityRec[5][1], entityRec[6][1], entityRec[7][1])
        S2 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}")'.format(
            entityRec[8][1], entityRec[9][1], entityRec[10][1], entityRec[11][1],
            entityRec[12][1], entityRec[13][1], entityRec[14][1])
        sql_string = r'INSERT INTO ENTTY VALUES(' + S1 + S2
        cEntity.execute(sql_string)
        clearRecArray(entityRec)


def writeAttrRec(attrRec):
    if not attrAR[18][1] is None:  # COLMN_NM
        S1 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            attrRec[0][1], attrRec[1][1], attrRec[2][1], attrRec[3][1],
            attrRec[4][1], attrRec[5][1], attrRec[6][1], attrRec[7][1])
        S2 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            attrRec[8][1], attrRec[9][1], attrRec[10][1], attrRec[11][1],
            attrRec[12][1], attrRec[13][1], attrRec[14][1], attrRec[15][1])
        S3 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            attrRec[16][1], attrRec[17][1], attrRec[18][1], attrRec[19][1],
            attrRec[20][1], attrRec[21][1], attrRec[22][1], attrRec[23][1])
        S4 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            attrRec[24][1], attrRec[25][1], attrRec[26][1], attrRec[27][1],
            attrRec[28][1], attrRec[29][1], attrRec[30][1], attrRec[31][1])
        S5 = '"{0}")'.format(attrAR[32][1])
        sql_string = 'INSERT INTO ATTRIB VALUES(' + S1 + S2 + S3 + S4 + S5
        cAttr.execute(sql_string)
        clearRecArray(attrRec)


def writeIndexRec(indexRec):
    if not indexRec[0][1] is None:  # IDX_ID
        S1 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            indexRec[0][1], indexRec[1][1], indexRec[2][1], indexRec[3][1],
            indexRec[4][1], indexRec[5][1], indexRec[6][1], indexRec[7][1])
        S2 = '"{0}", "{1}", "{2}", "{3}") '.format(
            indexRec[8][1], indexRec[9][1], indexRec[10][1], indexRec[11][1])
        sql_String = 'INSERT INTO IDX VALUES(' + S1 + S2
        cIndex.execute(sql_String)
        clearRecArray(indexRec)


def writeIdxMbrsRec(idxMbrsRec):
    if not idxMbrsRec[0][1] is None:  # IDX_ID
        sqlString = 'INSERT INTO IDX_MBRS values("{0}", "{1}", "{2}", "{3}")'.format(
            idxMbrsRec[0][1], idxMbrsRec[1][1], idxMbrsRec[2][1],
            idxMbrsRec[3][1])
        cIdxMbrs.execute(sqlString)
        clearRecArray(idxMbrsRec)


def writeRelRec(relRec):
    if not relRec[0][1] is None:  # REL_ID
        S1 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            relRec[0][1], relRec[1][1], relRec[2][1], relRec[3][1],
            relRec[4][1], relRec[5][1], relRec[6][1], relRec[7][1])
        S2 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}") '.format(
            relRec[8][1], relRec[9][1], relRec[10][1], relRec[11][1],
            relRec[12][1], relRec[13][1], relRec[14][1])
        sql_String = 'INSERT INTO RELSHP VALUES(' + S1 + S2
        cRlshp.execute(sql_String)
        clearRecArray(relRec)


def writeRelMbrsRec(relMbrsRec):
    if not relMbrsRec[0][1] is None:  # REL_ID
        S1 = '"{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", '.format(
            relMbrsRec[0][1], relMbrsRec[1][1], relMbrsRec[2][1], relMbrsRec[3][1],
            relMbrsRec[4][1], relMbrsRec[5][1], relMbrsRec[6][1], relMbrsRec[7][1])
        S2 = '"{0}", "{1}") '.format(relMbrsRec[8][1], relMbrsRec[9][1])
        sql_String = 'INSERT INTO RELSHP_MBRS VALUES(' + S1 + S2
        cRlMbrs.execute(sql_String)
        clearRecArray(relMbrsRec)


def writeSubjRec(subjRec):
    if not subjRec[0][1] is None:  # SUBJ_ID
        sql_String = 'INSERT INTO SUBJCT_AREA VALUES(' + \
                     '"{0}","{1}","{2}","{3}","{4}","{5}")'.format(
                         subjRec[0][1], subjRec[1][1],
                         subjRec[2][1], subjRec[3][1],
                         subjRec[4][1], subjRec[5][1])

        cSubjArea.execute(sql_String)
        clearRecArray(subjRec)


def writeDiagramRec(diagramRec):
    if not diagramAR[3][1] is None:  # SUBJ_ID
        sql_String = 'INSERT INTO DGRM VALUES(' + \
                     '"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}")'.format(
                         diagramRec[0][1], diagramRec[1][1],
                         diagramRec[2][1], diagramRec[3][1],
                         diagramRec[4][1], diagramRec[5][1],
                         diagramRec[6][1], diagramRec[7][1])
        cDiag.execute(sql_String)
        clearRecArray(diagramRec)


def flushOrphanRecords():
    writeModelRec(modelAR)
    writeEntityRec(entityAR)
    writeAttrRec(attrAR)
    writeIndexRec(indexAR)
    writeIdxMbrsRec(idxMbrsAR)
    writeRelRec(relAR)
    writeRelMbrsRec(relMbrsAR)
    writeSubjRec(subjAR)
    writeDiagramRec(diagramAR)


# noinspection PyInconsistentIndentation
def extractJson(_path, _filename):
    with open(_path + "/" + _filename, "r") as f:
        data = json.load(f)

    for record in data["MODEL"]:
        for key in record:
            # -- level 2 -------------------------------------------------------------
            if key == "ENTITIES":
                writeModelRec(modelAR)
                for entity in record["ENTITIES"]:
                    for entity_key in entity:
                        for x in range(0, len(entityAR)):
                            if entity_key == entityAR[x][0]:
                                entityAR[x][1] = entity[str(entity_key)]

                        # -- level 3  ------------------------------------------------
                        if entity_key == "ATTRIBUTES":
                            writeEntityRec(entityAR)
                            for attribute in entity[str(entity_key)]:
                                for item in attribute.items():
                                    (item_key, item_val) = item
                                    if item_key == attrAR[0][0]:
                                        if not attrAR[3][1] is None:  # COLMN_NM
                                            writeAttrRec(attrAR)
                                    for x in range(0, len(attrAR)):
                                        if item_key == attrAR[x][0]:
                                            attrAR[x][1] = item_val

                        # -- level 3  ------------------------------------------------
                        elif entity_key == "INDEXES":
                            writeAttrRec(attrAR)
                            for index in entity[str(entity_key)]:
                                for item in index.items():
                                    (item_key, item_val) = item
                                    if item_key == indexAR[0][0]:
                                        if not indexAR[0][1] is None:  # IDX_ID
                                            writeIndexRec(indexAR)
                                    for x in range(0, len(indexAR)):
                                        if item_key == indexAR[x][0]:
                                            indexAR[x][1] = item_val

                                    # --- level 4  -----------------------------------
                                    if item_key == "IDX_MBRS":
                                        hold_idx_id = indexAR[2][0]
                                        writeIndexRec(indexAR)
                                        for index_mbr in item_val:
                                            for mbr_item in index_mbr.items():
                                                (mitem_key, mitem_val) = mbr_item
                                                if mitem_key == idxMbrsAR[0][0]:
                                                    # MBR_ORDR_NUM always pop'd
                                                    if not idxMbrsAR[0][1] is None:
                                                        writeIdxMbrsRec(idxMbrsAR)
                                                    idxMbrsAR[0][1] = hold_idx_id
                                                for x in range(1, len(idxMbrsAR)):
                                                    if mitem_key == idxMbrsAR[x][0]:
                                                        idxMbrsAR[x][1] = mitem_val

            # -- level 2 -------------------------------------------------------------
            elif key == "RELATIONSHIPS":
                for relshp in record["RELATIONSHIPS"]:
                    for relshp_key in relshp:
                        if relshp_key == relAR[0][0]:
                            if not relAR[0][1] is None:  # RELSHP_ID
                                writeRelRec(relAR)
                        for x in range(0, len(relAR)):
                            if relshp_key == relAR[x][0]:
                                relAR[x][1] = relshp[str(relshp_key)]

                        # -- level 3  ------------------------------------------------
                        if relshp_key == "RELSHP_MBRS":
                            hold_rel_id = relAR[0][1]
                            writeRelRec(relAR)
                            for relMbrs in relshp[str(relshp_key)]:
                                for item in relMbrs.items():
                                    (item_key, item_val) = item
                                    if item_key == relMbrsAR[1][0]:  # PRNT_ATTRIB_ID
                                        if not relMbrsAR[0][1] is None:
                                            writeRelMbrsRec(relMbrsAR)
                                        relMbrsAR[0][1] = hold_rel_id
                                    for x in range(1, len(relMbrsAR)):
                                        if item_key == relMbrsAR[x][0]:
                                            relMbrsAR[x][1] = item_val

            # -- level 2 -------------------------------------------------------------
            elif key == "SUBJECT_AREAS":
                for subj_area in record["SUBJECT_AREAS"]:
                    for subj_key in subj_area:
                        if subj_key == subjAR[0][0]:  # SUBJCT_AREA_ID
                            if not subjAR[0][1] is None:
                                writeSubjRec(subjAR)
                        for x in range(0, len(subjAR)):
                            if subj_key == subjAR[x][0]:
                                subjAR[x][1] = subj_area[str(subj_key)]

                        # -- level 3  ------------------------------------------
                        if subj_key == "DIAGRAMS":
                            writeSubjRec(subjAR)
                            for diagram in subj_area[str(subj_key)]:
                                for item in diagram.items():
                                    (item_key, item_val) = item
                                    if item_key == diagramAR[0][0]:  # DGRM_ID
                                        if not diagramAR[0][1] is None:
                                            writeDiagramRec(diagramAR)
                                    for x in range(0, len(diagramAR)):
                                        if item_key == diagramAR[x][0]:
                                            diagramAR[x][1] = item_val
            else:
                # -- level 2 ------  MODEL ROOT KEYS
                for x in range(0, len(modelAR)):
                    if key == modelAR[x][0]:
                        modelAR[x][1] = record[str(key)]

    flushOrphanRecords()


# ====================================================================================
# -- Create Sqlite DB in Memory --
conn = sqlite3.connect(":memory:")

# -- Create MODEL (root) Table & Array --
cModel = conn.cursor()
sString = "CREATE TABLE MODEL (MODEL_FILE_NM, MODEL_NM, MODEL_VRSN_TXT," + \
          "APPL_NUM, CI_ID, CH_SRC_CD, " + \
          "MODEL_DEFN_TXT, TRGT_DBMS_NM, NSM_FILE_NM, " + \
          "MODEL_TEMPLT_NM, MODEL_AUTHOR_NM, MODEL_LOC)"
cModel.execute(sString)
modelAR = [['MODEL_FILE_NM', None], ['MODEL_NM', None], ['MODEL_VRSN_TXT', None],
           ['APPL_NUM', None], ['CI_ID', None], ['CH_SRC_CD', None],
           ['MODEL_DEFN_TXT', None], ['TRGT_DBMS_NM', None], ['NSM_FILE_NM', None],
           ['MODEL_TEMPLT_NM', None], ['MODEL_AUTHOR_NM', None], ['MODEL_LOC', None]
           ]

# -- Create ENTITY/ Table Table & Array --
cEntity = conn.cursor()
sString = "CREATE TABLE ENTTY(ENTTY_ID, MODEL_NM, MODEL_ID, ENTTY_NM, " + \
          "ENTTY_DEFN_TXT, TBL_NM, TBL_NM_HRDN_IND, DO_NOT_GEN_IND, " + \
          "TBL_CMMNT_TXT, SCHEMA_NM, PHY_ONLY_IND, LGCL_ONLY_IND, " + \
          "DATA_DOMAIN, EXTERNAL_PROPRIETARY, SET_MULTISET_OPT_TXT)"
cEntity.execute(sString)
entityAR = [['ENTTY_ID', None], ['MODEL_NM', None], ['MODEL_ID', None],
            ['ENTTY_NM', None], ['ENTTY_DEFN_TXT', None], ['TBL_NM', None],
            ['TBL_NM_HRDN_IND', None], ['DO_NOT_GEN_IND', None],
            ['TBL_CMMNT_TXT', None], ['SCHEMA_NM', None], ['PHY_ONLY_IND', None],
            ['LGCL_ONLY_IND', None], ['DATA_DOMAIN', None],
            ['EXTERNAL_PROPRIETARY', None], ['SET_MULTISET_OPT_TXT', None]
            ]

# -- Create ATTRIBUTE/ Column Table & Array --
cAttr = conn.cursor()
sString = "CREATE TABLE ATTRIB (ATTRIB_NM, ENTTY_NM, CDE_IND, RDE_IND, " + \
          "RDE_PII_IND, RDE_PHI_IND, RDE_PCI_IND, RDE_CignaIP, " + \
          "ColumnDataDomain, External_Proprietary, ATTRIB_DEFN_LGTH_NUM, " + \
          "ATTRIB_DEFN, ATTRIB_ORDR_NUM, ATTRIB_ID, ENTTY_ID, MODEL_NM, " + \
          "MODEL_ID, TBL_NM, COLMN_NM, COLMN_NM_HRDN_IND, DO_NOT_GEN_IND, " + \
          "LGCL_ONLY_IND, PHY_ONLY_IND, IS_PK_IND, IS_FK_IND, CMMNT_LGTH_NUM, " + \
          "COLMN_DTTY_TXT, DB_PHY_ORDR_NUM, COLMN_ORDR_NUM, COLMN_NULL_OPT, " + \
          "DEFLT_VAL_NM, DEFLT_VAL_TXT, COLMN_DEFN)"
cAttr.execute(sString)
attrAR = [['ATTRIB_NM', None], ['ENTTY_NM', None], ['CDE_IND', None],
          ['RDE_IND', None], ['RDE_PII_IND', None], ['RDE_PHI_IND', None],
          ['RDE_PCI_IND', None], ['RDE_CignaIP', None], ['ColumnDataDomain', None],
          ['External_Proprietary', None], ['ATTRIB_DEFN_LGTH_NUM', None],
          ['ATTRIB_DEFN', None], ['ATTRIB_ORDR_NUM', None], ['ATTRIB_ID', None],
          ['ENTTY_ID', None], ['MODEL_NM', None], ['MODEL_ID', None],
          ['TBL_NM', None], ['COLMN_NM', None], ['COLMN_NM_HRDN_IND', None],
          ['DO_NOT_GEN_IND', None], ['LGCL_ONLY_IND', None], ['PHY_ONLY_IND', None],
          ['IS_PK_IND', None], ['IS_FK_IND', None], ['CMMNT_LGTH_NUM', None],
          ['COLMN_DTTY_TXT', None], ['DB_PHY_ORDR_NUM', None],
          ['COLMN_ORDR_NUM', None], ['COLMN_NULL_OPT', None],
          ['DEFLT_VAL_NM', None], ['DEFLT_VAL_TXT', None], ['COLMN_DEFN', None]
          ]

# -- Create INDEX & INDEX Member Table & Array --
cIndex = conn.cursor()
sString = "CREATE TABLE IDX (IDX_ID, IDX_NM, IDX_LGCL_NM, ENTTY_ID, ENTTY_NM, MODEL_ID, " + \
          "MODEL_NM, IDX_TYPE_CD, DO_NOT_GEN_IND, IS_UNQ_IND, LGCL_ONLY_IND, " + \
          "PHY_ONLY_IND)"
cIndex.execute(sString)
indexAR = [['IDX_ID', None], ['IDX_NM', None], ['IDX_LGCL_NM', None], ['ENTTY_ID', None],
           ['ENTTY_NM', None], ['MODEL_ID', None], ['MODEL_NM', None],
           ['IDX_TYPE_CD', None], ['DO_NOT_GEN_IND', None], ['IS_UNQ_IND', None],
           ['LGCL_ONLY_IND', None], ['PHY_ONLY_IND', None]
           ]

cIdxMbrs = conn.cursor()
sString = "CREATE TABLE IDX_MBRS (MBR_IDX_ID, MBR_ORDR_NUM, ATTRIB_NM, COLMN_NM)"
cIdxMbrs.execute(sString)
idxMbrsAR = [['MBR_IDX_ID', None], ['MBR_ORDR_NUM', None], ['ATTRIB_NM', None],
             ['COLMN_NM', None]
             ]

# -- Create RELATIONSHIP & RELATIONSHIP Member Table & Array --
cRlshp = conn.cursor()
sString = "CREATE TABLE RELSHP (RELSHP_ID, RELSHP_NM, PRNT_ENTTY_ID, " + \
          "PRNT_ENTTY_NM, CHLD_ENTTY_ID, CHLD_ENTTY_NM, MODEL_ID, " + \
          "MODEL_NM, CRDNLTY_TY_TXT, DO_NOT_GEN_IND, RELSHP_TYPE_CD, " + \
          "PRNT_TBL_NM, CHLD_TBL_NM, IDX_ID, IDX_NM)"
cRlshp.execute(sString)
relAR = [['RELSHP_ID', None], ['RELSHP_NM', None], ['PRNT_ENTTY_ID', None],
         ['PRNT_ENTTY_NM', None], ['CHLD_ENTTY_ID', None],
         ['CHLD_ENTTY_NM', None], ['MODEL_ID', None], ['MODEL_NM', None],
         ['CRDNLTY_TY_TXT', None], ['DO_NOT_GEN_IND', None],
         ['RELSHP_TYPE_CD', None], ['PRNT_TBL_NM', None], ['CHLD_TBL_NM', None],
         ['IDX_ID', None], ['IDX_NM', None]
         ]

cRlMbrs = conn.cursor()
sString = "CREATE TABLE RELSHP_MBRS (MBR_RELSHP_ID, PRNT_ATTRIB_ID, " + \
          "PRNT_ATTRIB_NM, PRNT_COLMN_NM, PRNT_COLMN_DTTY_TXT, CHLD_ATTRIB_ID, " + \
          "CHLD_ATTRIB_NM, CHLD_COLMN_NM, CHLD_COLMN_DTTY_TXT, " + \
          "CHLD_COLMN_NULL_OPT_TXT)"
cRlMbrs.execute(sString)
relMbrsAR = [['MBR_RELSHP_ID', None], ['PRNT_ATTRIB_ID', None],
             ['PRNT_ATTRIB_NM', None], ['PRNT_COLMN_NM', None],
             ['PRNT_COLMN_DTTY_TXT', None], ['CHLD_ATTRIB_ID', None],
             ['CHLD_ATTRIB_NM', None], ['CHLD_COLMN_NM', None],
             ['CHLD_COLMN_DTTY_TXT', None], ['CHLD_COLMN_NULL_OPT_TXT', None]
             ]

# -- Create SUBJECT AREA Table & Array --
cSubjArea = conn.cursor()
sString = 'CREATE TABLE SUBJCT_AREA (SUBJCT_AREA_ID, SUBJCT_AREA_NM, MODEL_ID, ' + \
          'MODEL_NM, SUBJCT_AREA_DEFN_TXT, SUBJCT_AREA_AUTHOR_NM)'
cSubjArea.execute(sString)
subjAR = [['SUBJCT_AREA_ID', None], ['SUBJCT_AREA_NM', None], ['MODEL_ID', None],
          ['MODEL_NM', None], ['SUBJCT_AREA_DEFN_TXT', None],
          ['SUBJCT_AREA_AUTHOR_NM', None]
          ]

# -- Create DIAGRAM Table & Array --
cDiag = conn.cursor()
sString = "CREATE TABLE DGRM (DGRM_ID, DGRM_NM, MODEL_ID, SUBJCT_AREA_ID, " + \
          "SUBJCT_AREA_NM, MODEL_NM, DGRM_DEFN_TXT, DGRM_AUTHOR_NM)"
cDiag.execute(sString)
diagramAR = [['DGRM_ID', None], ['DGRM_NM', None], ['MODEL_ID', None],
             ['SUBJCT_AREA_ID', None], ['SUBJCT_AREA_NM', None],
             ['MODEL_NM', None], ['DGRM_DEFN_TXT', None],
             ['DGRM_AUTHOR_NM', None]
             ]
