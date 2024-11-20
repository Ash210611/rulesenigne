# Map of tags required for all taggable AWS resources. 
required_common_tags = {
  AppName          = "dataops-rules-engine"
  AssetOwner       = "Zachary.Hinds@CignaHealthcare.com"
}

# Map of tags required for data storage services. 
required_data_tags = {
  DataSubjectArea        = "provider"
  ComplianceDataCategory = "hipaa"
  DataClassification     = "confidential"
  BusinessEntity         = "evernorth"
  LineOfBusiness         = "government"
}

project_name   = "dataops-rules-engine"

# For additional details on Enterprise tagging requirements in the AWS Cloud
# please refer to: https://confluence.sys.cigna.com/display/CLOUD/Cloud+Tagging+Requirements+v2.0
