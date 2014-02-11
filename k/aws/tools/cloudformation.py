"""
CloudFormation tools support the following environment variables (from -h)

   --aws-credential-file VALUE
       Location of the file with your AWS credentials. This value can be set by
       using the environment variable 'AWS_CREDENTIAL_FILE'.

   --region VALUE
       Specify region VALUE as the web service region to use. This value can be
       set by using the environment variable 'EC2_REGION'.

CloudFormation tools are downloadable from:
     https://s3.amazonaws.com/cloudformation-cli/AWSCloudFormation-cli.zip
"""

import sh
import os.path
from k.aws.tools.base import ToolBase, TOOL_HOME, CONFIG_HOME

DOWNLOAD = TOOL_HOME + "/AWSCloudFormation-cli.zip"
AWS_CLOUDFORMATION_HOME = TOOL_HOME + "/AWSCloudFormation"

class CloudFormationTool(ToolBase):
	def name(self):
		return "CloudFormation tools"

	def download_tool(self):
		sh.mkdir("-p", TOOL_HOME)
		sh.rm("-f", DOWNLOAD)
		results = sh.wget("--no-check-certificate",
			"https://s3.amazonaws.com/cloudformation-cli/AWSCloudFormation-cli.zip",
			"-O", DOWNLOAD)

	def _return_path_bit(self, path):
		for p in path.split('/'):
			if p.startswith('AWSCloudFormation'):
				return p

	def install_tool(self):
		results = sh.unzip("-o", DOWNLOAD, "-d", TOOL_HOME)
		parts = results.split('\n')
		for part in parts:
			if part.find("inflating") > -1:
				path = self._return_path_bit(part.strip().split(" ")[1])
				break
		sh.rm("-f", AWS_CLOUDFORMATION_HOME)
		sh.ln("-s", TOOL_HOME + "/" + path, AWS_CLOUDFORMATION_HOME)
		self.rm_cmd_files(AWS_CLOUDFORMATION_HOME)

	def installed(self):
		return os.path.exists(AWS_CLOUDFORMATION_HOME)

	def paths(self):
		return ["$AWS_CLOUDFORMATION_HOME/bin"]

	def add_variables(self, region_aws_creds):
		aws_creds = region_aws_creds.creds
		region = region_aws_creds.region_name
		return {
			'AWS_CLOUDFORMATION_HOME': AWS_CLOUDFORMATION_HOME,
			'AWS_CREDENTIAL_FILE': "%s/%s/credential-file" % (
				CONFIG_HOME, aws_creds.env),
			'EC2_REGION': region
			}

	def file_config(self, region_aws_creds):
		aws_creds = region_aws_creds.creds
		sh.mkdir("-p", "%s/%s" % (CONFIG_HOME, aws_creds.env))
		filename = "%s/%s/credential-file" % (
			CONFIG_HOME, aws_creds.env)
		contents = '\n'.join([
			"AWSAccessKeyId=" + aws_creds.access,
			"AWSSecretKey=" + aws_creds.secret
		])
		return [{'filename': filename, 'contents': contents}]

	def sts_works(self):
		return False
