# pylint: disable=C0301		# Allow long lines
# pylint: disable=C0209		# Don't require formatted strings
# pylint: disable=R0902		# Don't limit the number of class attributes
# pylint: disable=R0903		# Don't require more public methods
# pylint: disable=R0913		# Allow more arguments
# pylint: disable=E1121		# Don't limit the number of positional arguments
#
# Author: 	Beverly De Loach
#
# History:	5/29/2020 SWC Adapting this to form base classes
#
# Source:	These class definitions are extracted from this file that is 
#		used by the Erwin extract, found here:
#		https://git.sys.cigna.com/imdevops/erwin_dm_api/blob/master/API%20Rules%20Engine%20Extract/erwinAPIMDExtract_Class_Definitions.py
#
# ===============================================================================
class Model_Extrt:
    '''
    Context = Root
    Connect to Persistence Object at ModelObject.Root level
    '''

    def __init__(self, model_id, model_nm, model_file_nm, model_path_txt):
        self.model_id = model_id
        self.model_nm = model_nm
        self.model_file_nm = model_file_nm
        self.model_path_txt = model_path_txt

        self.model_loc_txt = None
        self.model_defn_txt = None
        self.nsm_file_nm = None
        self.model_author_nm = None
        self.templt_nm = None
        self.CI_ID_udp = None
        # self.CH_SRC_CD_udp = None
        self.APPL_NUM_udp = None
        self.DBMS_vrsn_txt = None
        self.model_vrsn_txt = None
        self.model_schema_nm = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Model(Model_Extrt):
    def __init__(self, model_nm, model_defn_txt, model_file_nm,
                 nsm_file_nm, input_filename, input_filename_rel):
        # -- add model_loc_tx  bkd  10/28/2021

        super().__init__(
            model_id='UNKNOWN',
            model_nm=model_nm,
            model_file_nm=model_file_nm,
            model_path_txt='UNKNOWN')

        self.model_defn_txt = model_defn_txt

        if nsm_file_nm is None:
            self.nsm_file_nm = 'NONE ASSIGNED'
        else:
            self.nsm_file_nm = nsm_file_nm

        # try:
        # 	self.nsm_file_nm	= nsm_file_nm
        # except:
        # 	self.nsm_file_nm	= 'NONE ASSIGNED'
        # 	raise

        self.filenum = 0
        # The Data Model Rules Engine only reads 1 JSON file.

        # Keep track of which input file this entity came from
        self.input_filename = input_filename
        self.input_filename_rel = input_filename_rel

    def get_filenum(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.filenum
        return None

    def get_input_filename_rel(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.input_filename_rel
        return None

    def __repr__(self):
        '''
        This function is handy for debugging.
        This function is called if you want to print a class instance.
        Usage: print (G.MODEL)
        '''

        line = '\n' + ('-' * 80) + '\n'
        line += 'Model\n'
        line += '---------------\n'
        line += f'Model ID          : {self.model_id}\n'
        line += f'Model Name        : {self.model_nm}\n'
        line += f'Model File Name   : {self.model_file_nm}\n'
        line += f'Model Path Txt    : {self.model_path_txt}\n'
        line += 'Model Defn Txt    : {0}\n'.format(
            self.model_defn_txt[:20] + (self.model_defn_txt[20:] and '...'))
        line += f'Input Filename    : {self.input_filename}\n'
        line += f'Input Filename Rel: {self.input_filename_rel}\n'

        return line


# ===============================================================================
class Table_Extrt:
    def __init__(self, model_nm, model_id, entty_nm, entty_id, entty_defn_txt):
        self.model_id = model_id
        self.model_nm = model_nm
        self.entty_defn_txt = entty_defn_txt
        self.entty_id = entty_id
        self.entty_nm = entty_nm

        self.tbl_nm = None
        self.tbl_cmmnt_txt = None
        self.tbl_schema_nm = None
        self.phy_only_ind = None
        self.lgcl_only_ind = None
        self.tbl_nm_hrdnd_ind = None
        self.do_not_gen_ind = None
        self.DataDomain_udp = None
        self.External_Proprietary_udp = None
        self.SetMultiSet_Opt_txt = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ==============================================================================
class Entity(Table_Extrt):
    def __init__(self, model_nm, model_id, entty_nm, entty_id,
                 entty_defn_txt, DataDomain_udp, tbl_nm,
                 input_filename,
                 input_filename_rel):

        super().__init__(
            entty_id=entty_id,
            entty_nm=entty_nm,
            model_id=model_id,
            model_nm=model_nm,
            entty_defn_txt=entty_defn_txt
        )
        self.DataDomain_udp = DataDomain_udp
        self.tbl_nm = tbl_nm

        # Keep track of which input file this entity came from
        self.input_filename = input_filename
        self.input_filename_rel = input_filename_rel

        self.entty_nm_tokens = entty_nm.split(' ')

        self.filenum = 0

    # The Data Model Rules Engine only reads 1 JSON file.

    def get_filenum(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.filenum
        return None

    def get_input_filename_rel(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.input_filename_rel
        return None

    def __repr__(self):
        '''
        This function is handy for debugging.
        This function is called if you want to print a class instance.
        Usage: print (G.ENTITY)
        '''

        line = '\n' + ('-' * 80) + '\n'
        line += 'Entity\n'
        line += '---------------\n'
        line += 'Entity ID         : {0}\n'.format(
            self.entty_id)
        line += 'Entity Name       : {0}\n'.format(
            self.entty_nm)
        line += 'Model ID          : {0}\n'.format(
            self.model_id)
        line += 'Model Name        : {0}\n'.format(
            self.model_nm)
        line += 'Input Filename    : {0}\n'.format(
            self.input_filename)
        line += 'Input Filename Rel: {0}\n'.format(
            self.input_filename_rel)
        return line


# ===============================================================================
class Column_Extrt:
    def __init__(self, model_id, model_nm, colmn_null_opt_txt,
                 deflt_val_nm, deflt_val_txt, attrib_id, entty_id):
        self.attrib_id = attrib_id
        self.attrib_nm = entty_id
        self.model_id = model_id
        self.model_nm = model_nm
        self.colmn_null_opt_txt = colmn_null_opt_txt
        self.deflt_val_nm = deflt_val_nm
        self.deflt_val_txt = deflt_val_txt

        self.entty_id = None
        self.entty_nm = None
        self.attrib_defn_txt = None
        self.column_nm = None
        self.tbl_nm = None
        self.colmn_cmmnt_txt = None
        self.colmn_nm_hrdnd_ind = None
        self.attrib_defn_lgth = None
        self.colmn_cmmnt_lgth = None
        self.colmn_data_type_txt = None
        self.lgcl_only_ind = None
        self.phy_only_ind = None
        self.is_PK_ind = None
        self.is_FK_ind = None
        self.DB_phy_ordr_num = None
        self.colmn_phy_ordr_num = None
        self.attrib_ordr_num = None
        self.do_not_gen_ind = None
        self.CDE_udp = None
        self.RDE_udp = None
        self.RDE_PII_udp = None
        self.RDE_PHI_udp = None
        self.RDE_PCI_udp = None
        self.RDE_CignaIP_udp = None
        self.ColumnDataDomain_udp = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ==============================================================================
class Attrib(Column_Extrt):
    def __init__(self, model_id, model_nm, colmn_null_opt_txt,
                 deflt_val_nm, deflt_val_txt, attrib_id, attrib_nm, attrib_defn_txt, entty_id,
                 input_filename,
                 input_filename_rel):

        super().__init__(
            attrib_id=attrib_id,
            model_id=model_id,
            model_nm=model_nm,
            colmn_null_opt_txt=colmn_null_opt_txt,
            deflt_val_nm=deflt_val_nm,
            deflt_val_txt=deflt_val_txt,
            entty_id=entty_id
        )

        self.tbl_nm = None
        self.entty_nm = None
        self.entty_defn_txt = None
        self.colmn_cmmnt_txt = None
        self.colmn_nm = None
        self.colmn_nm_hrdnd_ind = None
        self.colmn_data_type_txt = None
        self.attrib_nm = attrib_nm
        self.attrib_defn_txt = attrib_defn_txt

        # Keep track of which input file this entity came from
        self.input_filename = input_filename
        self.input_filename_rel = input_filename_rel

        self.attr_nm_tokens = attrib_nm.split(' ')

        self.filenum = 0

    # The Data Model Rules Engine only reads 1 JSON file.

    def get_filenum(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.filenum
        return None

    def get_input_filename_rel(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.input_filename_rel
        return None

    def __repr__(self):
        '''
        This function is handy for debugging.
        This function is called if you want to print a class instance.
        Usage: print (G.ATTRIB)
        '''

        line = '\n' + ('-' * 80) + '\n'
        line += 'Attribute\n'
        line += '---------------\n'
        line += 'Attribute ID         : {0}\n'.format(
            self.attrib_id)
        line += 'Attribute Name       : {0}\n'.format(
            self.attrib_nm)
        line += 'Model ID          : {0}\n'.format(
            self.model_id)
        line += 'Model Name        : {0}\n'.format(
            self.model_nm)
        line += 'Input Filename    : {0}\n'.format(
            self.input_filename)
        line += 'Input Filename Rel: {0}\n'.format(
            self.input_filename_rel)
        return line


# ===============================================================================
class Relshp_Extrt:
    '''
    relationship is based on child entity, which has parent entity id
             as well as link to relationship object.
    '''

    def __init__(self, prnt_relshp_ref, model_id, model_nm):
        self.model_id = model_id
        self.model_nm = model_nm
        self.relshp_id = prnt_relshp_ref

        self.relshp_nm = None
        self.prnt_entty_id = None
        self.prnt_entty_nm = None
        self.prnt_attrib_nm = None
        self.prnt_attrib_id = None
        self.prnt_colmn_nm = None
        self.prnt_colmn_data_type_txt = None
        self.chld_entty_id = None
        self.chld_entty_nm = None
        self.chld_attrib_nm = None
        self.chld_attrib_id = None
        self.chld_colmn_nm = None
        self.chld_colmn_data_type_txt = None
        self.chld_colmn_null_opt_txt = None
        self.crdnlty_type_txt = None
        self.relshp_type_cd = None
        self.do_not_gen_ind = None
        self.prnt_tbl_nm = None
        self.chld_tbl_nm = None
        self.ndx_id = None
        self.ndx_nm = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Relshp(Relshp_Extrt):

    def __init__(self, relshp_nm, prnt_relshp_ref, model_id, model_nm):
        super().__init__(prnt_relshp_ref, model_id, model_nm)
        self.relshp_nm = relshp_nm

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Subjct_Area_Extrt:
    def __init__(self, model_id, model_nm):
        self.model_id = model_id
        self.model_nm = model_nm

        self.subjct_area_id = None
        self.subjct_area_nm = None
        self.subjct_area_defn_txt = None
        self.subjct_area_author_nm = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Subjct_Area(Subjct_Area_Extrt):

    def __init__(self, model_id, model_nm, subjct_area_id, subjct_area_nm,
                 subjct_area_defn_txt, subjct_area_author_nm):
        super().__init__(model_id, model_nm)

        self.model_id = model_id
        self.model_nm = model_nm
        self.subjct_area_id = subjct_area_id
        self.subjct_area_nm = subjct_area_nm
        self.subjct_area_defn_txt = subjct_area_defn_txt
        self.subjct_area_author_nm = subjct_area_author_nm

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Idx_Extrt:
    def __init__(self, model_id, model_nm):
        self.model_id = model_id
        self.model_nm = model_nm

        self.idx_id = None
        self.idx_nm = None
        self.entty_id = None
        self.entty_nm = None
        self.idx_type_cd = None
        self.do_not_gen_ind = None
        self.is_unique_ind = None
        self.logical_only_ind = None
        self.physical_only_ind = None
        self.idx_members = []  # one or more: [K:V att_nm, colmn_nm, idx_order_num]
        self.idx_excel_members = []
        self.idx_lgcl_nm = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Dgrm_Extrt:
    def __init__(self, model_id, model_nm):
        self.model_id = model_id
        self.model_nm = model_nm

        self.dgrm_id = None
        self.dgrm_nm = None
        self.subjct_area_id = None
        self.subjct_area_nm = None
        self.dgrm_defn_txt = None
        self.dgrm_author_nm = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line

# ===============================================================================
