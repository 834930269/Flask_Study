from wtforms.validators import Required
from flask_wtf import FlaskForm
from wtforms import SelectField,BooleanField,StringField, SubmitField,TextAreaField
from wtforms import ValidationError
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from ..models import User,Role
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from .. import photos
class NameForm(FlaskForm):
    name=StringField('你的名字?',validators=[Required()])
    submit=SubmitField('提交')
	
class EditProfileForm(FlaskForm):
	name = StringField('解放真名',validators=[Length(0,64)])
	location = StringField('所在地',validators=[Length(0,64)])
	about_me = TextAreaField('关于我')
	submit = SubmitField('提交')

class EditProfileAdminForm(FlaskForm):
	email = StringField('邮箱',validators=[Required(),Length(1,64),Email()])
	username = StringField('昵称',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'用户名至少有一个字母,数字,小数点和下划线.')])
	confirmed = BooleanField('邮箱确认')
	role = SelectField('权限',coerce=int)
	name = StringField('真实姓名',validators=[Length(0,64)])
	location = StringField('所在地',validators=[Length(0,64)])
	about_me = TextAreaField('关于')
	submit = SubmitField('提交')

	def __init__(self,user,*args,**kwargs):
		super(EditProfileAdminForm,self).__init__(*args,**kwargs)
		self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self,field):
		#如果字段没有改变就跳过验证
		if field.data != self.user.email and User.query.filter_by(email=field.data).first():
			raise  ValidationError('邮箱已被注册.')

	def validate_username(self,field):
		if field.data != self.user.username and User.query.filter_by(username=field.data).first():
			raise ValidationError('昵称已被使用.')

class UploadForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, u'只能上传图片！'), 
        FileRequired(u'请选择一个头像吧！')])
    submit = SubmitField(u'确认上传',render_kw={"class":"btn btn-primary"})
