from storages.backends.s3boto3 import S3Boto3Storage

class CustomMediaS3Boto3Storage(S3Boto3Storage):
    file_overwrite = False
    
    def _save(self, name, content):
        file_directorys = ["folder_name/", "folder_name\\"]
        
        if any(directory in name for directory in file_directorys):
            default_acl = "public-read"
        else: 
            default_acl = "private"
        
        return super()._save(name, content)