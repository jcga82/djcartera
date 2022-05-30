from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import password_validation, authenticate
from django.core.validators import RegexValidator, FileExtensionValidator
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from micartera.models import *


class EmpresaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = (
            'id',
            'nombre',
            'symbol',
            'logo',
            'isin',
            'description',
            'estrategia',
            'sector',
            'pais',
            'tipo',
            'dividendo_desde',
            'fechas_dividendo',
            'cagr3',
            'cagr5',
            'pub_date'
        )

class EmpresaSerializer(serializers.Serializer):

    nombre = serializers.CharField()
    symbol = serializers.CharField()

    def create(self, data):
        emp = Empresa.objects.create(**data)
        return emp

#DIVIDENDOS EMPRESAS
class DividendoEmpresaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DividendoEmpresa
        fields = (
            # 'empresa',
            'date',
            'dividendo'
        )
class DividendoEmpresaSerializer(serializers.Serializer):
    # empresa = serializers.CharField()
    date = serializers.CharField()
    dividendo = serializers.FloatField()

    def create(self, data):
        div = DividendoEmpresa.objects.create(**data)
        return div

#FUNDAMENTALES EMPRESAS
class FundamentalesEmpresaModelSerializer(serializers.ModelSerializer):
    # empresa_nombre = serializers.RelatedField(source='empresa', read_only=True)
    # empresa_set = EmpresaModelSerializer(many=True)
    class Meta:
        model = FundamentalesEmpresa
        fields = '__all__'

class FundamentalesEmpresaSerializer(serializers.Serializer):
    # empresa = serializers.CharField()
    fiscalDateEnding = serializers.CharField()
    # dividendo = serializers.FloatField()

    def create(self, data):
        fun = FundamentalesEmpresa.objects.create(**data)
        return fun

#HISTORICOS EMPRESAS
class HistoricoEmpresaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoEmpresa
        fields = '__all__'
        
class HistoricoEmpresaSerializer(serializers.Serializer):
    # empresa = serializers.CharField()
    fiscalDateEnding = serializers.CharField()
    # dividendo = serializers.FloatField()

    def create(self, data):
        his = HistoricoEmpresa.objects.create(**data)
        return his

#QHISTORICOS EMPRESAS
class QHistoricoEmpresaModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = QHistoricoEmpresa
        fields = '__all__'
        depth = 2
        
class QHistoricoEmpresaSerializer(serializers.Serializer):
    # empresa = serializers.CharField()
    fiscalDateEnding = serializers.CharField()
    # dividendo = serializers.FloatField()

    def create(self, data):
        his = QHistoricoEmpresa.objects.create(**data)
        return his

#CARTERA
class CarteraModelSerializer(serializers.ModelSerializer):
    # viviendas = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Cartera
        fields = (
            'nombre',
            'capital_inicial',
            # 'viviendas'
        )
        
class CarteraSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    capital_inicial = serializers.FloatField()

    def create(self, data):
        car = Cartera.objects.create(**data)
        return car

#VIVIENDAS
class ViviendaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vivienda
        depth = 2
        fields = (
            'id',
            'cartera',
            'tipo',
            'direccion',
            'comunidad',
            'valor_cv',
            'gastos_cv',
            'gastos_reforma',
            'ingresos_mensuales',
            'gastos_ibi',
            'gastos_seguros',
            'gastos_comunidad',
            'financiacion',
            'pct_finan',
            'plazo',
            'interes',
            'itp', 
            'total_compra', 
            'gastos_anuales',
            'rent_bruta',
            'rent_neta', 
            'valor_hipoteca', 
            'capital_aportar', 
            'cuota_hipoteca_mes', 
            'cash_flow', 
            'roce'
        )
        
class ViviendaSerializer(serializers.Serializer):
    # cartera = CarteraSerializer()
    cartera_id = serializers.IntegerField()
    tipo = serializers.CharField()
    direccion = serializers.CharField()
    comunidad = serializers.CharField()
    valor_cv = serializers.FloatField()
    gastos_cv = serializers.FloatField()
    gastos_reforma = serializers.FloatField()
    ingresos_mensuales = serializers.FloatField()
    gastos_ibi = serializers.FloatField()
    gastos_seguros = serializers.FloatField()
    gastos_comunidad = serializers.FloatField()
    financiacion = serializers.FloatField()

    def create(self, data):
        return Vivienda.objects.create(**data)

#CRIPTO FUNDAMENTALES Y ANALISIS
class FundamentalesCriptoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundamentalesCripto
        fields = '__all__'
        depth = 1
        
class FundamentalesCriptoSerializer(serializers.Serializer):
    def create(self, data):
        return FundamentalesCripto.objects.create(**data)

class CriptoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cripto
        fields = '__all__'
        
class CriptoSerializer(serializers.Serializer):
    def create(self, data):
        return Cripto.objects.create(**data)

class AnalisisCriptoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalisisCripto
        fields = '__all__'
        depth = 1
        
class AnalisisCriptoSerializer(serializers.Serializer):
    def create(self, data):
        return AnalisisCripto.objects.create(**data)

#HISTORICO CASILLAS
class HistoricoCasillasModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoCasillas
        fields = '__all__'
        
class HistoricoCasillasSerializer(serializers.Serializer):
    # empresa = serializers.CharField()
    fiscalDateEnding = serializers.CharField()
    # dividendo = serializers.FloatField()

    def create(self, data):
        his = HistoricoCasillas.objects.create(**data)
        return his


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="micartera:user-detail")
    class Meta:
        model = User
        fields = ['username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class UserLoginSerializer(serializers.Serializer):

    # Campos que vamos a requerir
    # email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(min_length=6, max_length=64)

    # Primero validamos los datos
    def validate(self, data):

        # authenticate recibe las credenciales, si son válidas devuelve el objeto del usuario
        user = authenticate(username=data['username'], password=data['password'])
        print(user)
        if not user:
            raise serializers.ValidationError('Las credenciales no son válidas')

        # Guardamos el usuario en el contexto para posteriormente en create recuperar el token
        self.context['user'] = user
        return data

    def create(self, data):
        """Generar o recuperar token."""
        token, created = Token.objects.get_or_create(user=self.context['user'])
        return self.context['user'], token.key


class UserSignUpSerializer(serializers.Serializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    photo = serializers.ImageField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], 
        required=False
    )

    extract = serializers.CharField(max_length=1000, required=False)

    city = serializers.CharField(max_length=250, required=False)

    country = serializers.CharField(max_length=250, required=False)

    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="Debes introducir un número con el siguiente formato: +999999999. El límite son de 15 dígitos."
    )
    phone = serializers.CharField(validators=[phone_regex], required=False)

    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    first_name = serializers.CharField(min_length=2, max_length=50)
    last_name = serializers.CharField(min_length=2, max_length=100)

    def validate(self, data):
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        password_validation.validate_password(passwd)

        image = None
        if 'photo' in data:
            image = data['photo']

        if image:
            if image.size > (512 * 1024):
                raise serializers.ValidationError(f"La imagen es demasiado grande, el peso máximo permitido es de 512KB y el tamaño enviado es de {round(image.size / 1024)}KB")

        return data

    def create(self, data):
        data.pop('password_confirmation')
        user = User.objects.create_user(**data)
        return user