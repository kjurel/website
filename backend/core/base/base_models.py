from tortoise import fields, models


class BaseDB(models.Model):
  id = fields.IntField(pk=True, index=True)
  created_at = fields.DatetimeField(auto_now_add=True)
  updated_at = fields.DatetimeField(auto_now=True)
  
  async def to_dict(self) -> dict:
    d = {}
    
    for field in self._meta.db_fields:
      d[field] = getattr(self, field)
    
    for field in self._meta.backward_fk_fields:
      d[field] = await getattr(self, field).all().values()
    
    return d
  
  class Meta:
    abstract = True


import bcrypt


class BaseUser(BaseDB):
  id: str = fields.UUIDField(pk=True)                       # type: ignore[assignment]
  username: str = fields.CharField(max_length=20, null=False, unique=True)
  passhash: bytes = fields.BinaryField(max_length=128, null=False)
  
  class Meta:
    abstract = True
  
  def verify_password(self, password: bytes) -> bool:
    return bcrypt.checkpw(password=password, hashed_password=self.passhash)
  
  async def save_passhash(self, password: bytes) -> None:
    await self.update_from_dict(
        dict(passhash=bcrypt.hashpw(password=password,
                                    salt=bcrypt.gensalt()))
    ).save()
