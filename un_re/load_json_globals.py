# pylint: disable=C0209           # Don't require formtted strings

import un_re.class_definitions_base as B
import un_re.global_shared_variables as G
import un_re.extractModelJson as J

from un_re.indent_info import indent_info


# ===============================================================================
def load_MODELS():
    # Load G.MODELS from sqlite table

    J.cModel.execute("SELECT COUNT(*) from MODEL ")
    KNTR = J.cModel.fetchone()[0]

    sql = "Select " + \
          "MODEL_FILE_NM, MODEL_NM, MODEL_VRSN_TXT," + \
          "APPL_NUM, CI_ID, CH_SRC_CD, " + \
          "MODEL_DEFN_TXT, TRGT_DBMS_NM, NSM_FILE_NM, " + \
          "MODEL_TEMPLT_NM, MODEL_AUTHOR_NM, MODEL_LOC " + \
          "From MODEL " + \
          "Order by MODEL_NM"

    J.cModel.execute(sql)

    for _ in range(0, KNTR):
        (MODEL_FILE_NM, MODEL_NM,
         _,  # MODEL_VRSN_TXT,
         _,  # APPL_NUM,
         _,  # CI_ID,
         _,  # CH_SRC_CD,
         MODEL_DEFN_TXT,
         _,  # TRGT_DBMS_NM,
         NSM_FILE_NM,
         _,  # MODEL_TEMPLT_NM,
         _,  # MODEL_AUTHOR_NM,
         _  # MODEL_LOC
         ) = J.cModel.fetchone()

        G.MODEL = B.Model(MODEL_NM,
                          MODEL_DEFN_TXT,
                          MODEL_FILE_NM,
                          NSM_FILE_NM,
                          G.INPUT_FILENAME,
                          G.INPUT_FILENAME_REL)

        G.MODELS.append(G.MODEL)

    if G.VERBOSE:
        indent_info('Num Models   found: {0}'.format(
            len(G.MODELS)))


# print (G.MODELS)	# If desired for debugging

# ===============================================================================
def load_ENTITIES():
    # Load G.ENTITIES from sqlite table
    J.cEntity.execute("SELECT COUNT(*) from ENTTY")
    KNTR = J.cEntity.fetchone()[0]

    sql = "Select " + \
          "ENTTY_ID, MODEL_NM, MODEL_ID, ENTTY_NM, " + \
          "ENTTY_DEFN_TXT, TBL_NM, TBL_NM_HRDN_IND, DO_NOT_GEN_IND, " + \
          "TBL_CMMNT_TXT, SCHEMA_NM, PHY_ONLY_IND, LGCL_ONLY_IND, " + \
          "DATA_DOMAIN, EXTERNAL_PROPRIETARY, SET_MULTISET_OPT_TXT " + \
          "From ENTTY " + \
          "ORDER BY ENTTY_ID"

    J.cEntity.execute(sql)

    for _ in range(0, KNTR):
        (ENTTY_ID, MODEL_NM, MODEL_ID, ENTTY_NM,
         ENTTY_DEFN_TXT, TBL_NM,
         _,  # TBL_NM_HRDN_IND,
         _,  # DO_NOT_GEN_IND,
         _,  # TBL_CMMNT_TXT,
         _,  # SCHEMA_NM,
         _,  # PHY_ONLY_IND,
         _,  # LGCL_ONLY_IND,
         DATA_DOMAIN,
         _,  # EXTERNAL_PROPRIETARY,
         _  # SET_MULTISET_OPT_TXT
         ) = J.cEntity.fetchone()

        G.ENTITY = B.Entity(MODEL_NM, MODEL_ID,
                            ENTTY_NM, ENTTY_ID,
                            ENTTY_DEFN_TXT,
                            DATA_DOMAIN,
                            TBL_NM,
                            G.INPUT_FILENAME,
                            G.INPUT_FILENAME_REL)

        G.ENTITIES.append(G.ENTITY)

    if G.VERBOSE:
        indent_info('Num Entities found: {0}'.format(
            len(G.ENTITIES)))


# print (G.ENTITIES)	# If desired for debugging

# ===============================================================================
def load_SUBJCT_AREAS():
    # Load G.SUBJCT_AREAS from sqlite table

    J.cSubjArea.execute("SELECT COUNT(*) from SUBJCT_AREA ")
    KNTR = J.cSubjArea.fetchone()[0]
    # cursor = J.cSubjArea.execute('select * from SUBJCT_AREA')

    sqlString = "SELECT MODEL_NM, SUBJCT_AREA_NM, SUBJCT_AREA_DEFN_TXT," + \
                "SUBJCT_AREA_AUTHOR_NM  " + \
                "From SUBJCT_AREA " + \
                "Order by MODEL_NM, SUBJCT_AREA_NM"

    J.cSubjArea.execute(sqlString)

    for _ in range(0, KNTR):
        (MODEL_NM, SUBJCT_AREA_NM, SUBJCT_AREA_DEFN_TXT,
         SUBJCT_AREA_AUTHOR_NM) = J.cSubjArea.fetchone()

        G.SUBJCT_AREA = B.Subjct_Area(MODEL_NM,
                                      SUBJCT_AREA_NM, SUBJCT_AREA_DEFN_TXT,
                                      SUBJCT_AREA_AUTHOR_NM,
                                      G.INPUT_FILENAME,
                                      G.INPUT_FILENAME_REL)

        G.SUBJCT_AREAS.append(G.SUBJCT_AREA)

    if G.VERBOSE:
        indent_info('Num Subject Areas   found: {0}'.format(
            len(G.SUBJCT_AREAS)))


# print (G.SUBJCT_AREAS)      # If desired for debugging

# ===============================================================================
def load_json_globals():
    load_MODELS()
    load_ENTITIES()
    load_SUBJCT_AREAS()

# Add functions here to load columns, indexes, etc from the Erwin Extract
