# import boto3
# from django.conf import settings
# import os


# class Bucket:
#     """
#     CDN Bucket manager

#     NOTE:
#     none of these methods are async.
#     use public interface in task.py modules instead.
#     """

#     def __init__(self):
#         session = boto3.session.Session()
#         self.conn = session.client(
#             service_name="s3",
#             aws_access_key_id=os.environ["ARVAN_ACCESS_KEY"],
#             aws_secret_access_key=os.environ["ARVAN_SECRET_KEY"],
#             endpoint_url=os.environ["ARVAN_ENDPOINT_URL"],
#             region_name=os.environ["ARVAN_REGION"],
#         )

    
#     def get_objects(self):
#         bucket_name = os.environ["ARVAN_STORAGE_BUCKET_NAME"]
#         result = self.conn.list_objects_v2(Bucket=bucket_name)
#         if result['KeyCount']:
#             return result ['Content']
#         else:
#             return result
    
# bucket = Bucket()

