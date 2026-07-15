# Módulo de Clientes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar cadastro, consulta, edição e inativação de clientes com validação de CPF/CNPJ e controle de permissões.

**Architecture:** O módulo será separado em modelo, schemas, repository, service e router. O service concentra validações de documento, duplicidade e regras de inativação. O router converte erros de domínio em respostas HTTP e aplica as permissões por perfil.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy Async, PostgreSQL 17, Pydantic, Alembic, Pytest, Docker Compose.

## Global Constraints

- `customer_type`: `INDIVIDUAL` ou `COMPANY`.
- `document_type`: `CPF` ou `CNPJ`.
- O campo `document` deve ser único.
- O documento deve ser armazenado somente com dígitos.
- CPF e CNPJ devem ser validados conforme o tipo.
- O endereço principal fica na tabela `customers`.
- Clientes inativos permanecem no banco.
- Clientes inativos não podem ser usados em novos pedidos.
- `ADMINISTRADOR`, `PRODUTOR` e `VENDEDOR` podem consultar, criar e editar.
- Somente `ADMINISTRADOR` e `PRODUTOR` podem inativar.
- Exclusão física não será implementada.

---

## File Structure

### Novos arquivos

- `backend/app/modules/customers/__init__.py`
- `backend/app/modules/customers/customer_model.py`
- `backend/app/modules/customers/customer_schemas.py`
- `backend/app/modules/customers/customer_repository.py`
- `backend/app/modules/customers/customer_service.py`
- `backend/app/api/routers/customers.py`
- `backend/app/migrations/versions/0007_create_customers.py`
- `backend/tests/test_customer_model.py`
- `backend/tests/test_customer_schemas.py`
- `backend/tests/test_customer_service.py`
- `backend/tests/test_customers_api.py`
- `backend/tests/test_customer_migration.py`

### Arquivos modificados

- `backend/app/api/dependencies.py`
- `backend/app/main.py`

---

### Task 1: Modelo e enums de cliente

**Files:**
- Create: `backend/app/modules/customers/__init__.py`
- Create: `backend/app/modules/customers/customer_model.py`
- Test: `backend/tests/test_customer_model.py`

**Interfaces:**
- Produces:
  - `CustomerType`
  - `DocumentType`
  - `Customer`

- [ ] **Step 1: Criar o teste do modelo**

Criar `backend/tests/test_customer_model.py`:

```python
from app.modules.customers.customer_model import (
    Customer,
    CustomerType,
    DocumentType,
)


def test_customer_table_name() -> None:
    assert Customer.__tablename__ == "customers"


def test_customer_type_values() -> None:
    assert {item.value for item in CustomerType} == {
        "INDIVIDUAL",
        "COMPANY",
    }


def test_document_type_values() -> None:
    assert {item.value for item in DocumentType} == {
        "CPF",
        "CNPJ",
    }
```

- [ ] **Step 2: Rodar e confirmar falha**

No PC principal:

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_customer_model.py -v
```

Esperado: erro de importação porque o módulo ainda não existe.

- [ ] **Step 3: Criar o pacote**

Criar `backend/app/modules/customers/__init__.py` vazio.

- [ ] **Step 4: Implementar o modelo**

Criar `backend/app/modules/customers/customer_model.py`:

```python
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CustomerType(StrEnum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"


class DocumentType(StrEnum):
    CPF = "CPF"
    CNPJ = "CNPJ"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    customer_type: Mapped[CustomerType] = mapped_column(
        Enum(
            CustomerType,
            name="customer_type",
        ),
        nullable=False,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(
            DocumentType,
            name="customer_document_type",
        ),
        nullable=False,
    )

    document: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(254),
        nullable=True,
    )

    street: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    complement: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    neighborhood: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(2),
        nullable=True,
    )

    zip_code: Mapped[str | None] = mapped_column(
        String(8),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

- [ ] **Step 5: Rodar os testes**

```powershell
python -m pytest tests\test_customer_model.py -v
```

Esperado: 3 testes passando.

- [ ] **Step 6: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\modules\customers backend\tests\test_customer_model.py
git commit -m "feat: adiciona modelo de clientes"
```

---

### Task 2: Schemas e normalização dos dados

**Files:**
- Create: `backend/app/modules/customers/customer_schemas.py`
- Test: `backend/tests/test_customer_schemas.py`

**Interfaces:**
- Produces:
  - `CustomerCreate`
  - `CustomerUpdate`
  - `CustomerRead`
  - `CustomerStatusUpdate`
  - `digits_only(value: str | None) -> str | None`

- [ ] **Step 1: Criar os testes dos schemas**

Criar `backend/tests/test_customer_schemas.py`:

```python
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.customers.customer_model import (
    CustomerType,
    DocumentType,
)
from app.modules.customers.customer_schemas import (
    CustomerCreate,
    CustomerStatusUpdate,
)


def test_customer_create_normalizes_document_and_zip_code() -> None:
    payload = CustomerCreate(
        customer_type=CustomerType.INDIVIDUAL,
        document_type=DocumentType.CPF,
        document="529.982.247-25",
        name="Cliente Teste",
        phone="(67) 99999-9999",
        zip_code="79000-000",
        state="ms",
    )

    assert payload.document == "52998224725"
    assert payload.phone == "67999999999"
    assert payload.zip_code == "79000000"
    assert payload.state == "MS"


def test_customer_create_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        CustomerCreate(
            customer_type=CustomerType.INDIVIDUAL,
            document_type=DocumentType.CPF,
            document="52998224725",
            name="   ",
        )


def test_customer_status_update_accepts_boolean() -> None:
    payload = CustomerStatusUpdate(is_active=False)
    assert payload.is_active is False
```

- [ ] **Step 2: Rodar e confirmar falha**

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_customer_schemas.py -v
```

Esperado: erro de importação.

- [ ] **Step 3: Implementar os schemas**

Criar `backend/app/modules/customers/customer_schemas.py`:

```python
import re
from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.modules.customers.customer_model import (
    CustomerType,
    DocumentType,
)


def digits_only(value: str | None) -> str | None:
    if value is None:
        return None

    return re.sub(r"\D", "", value)


class CustomerBase(BaseModel):
    customer_type: CustomerType
    document_type: DocumentType
    document: str = Field(min_length=11, max_length=18)
    name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    street: str | None = Field(default=None, max_length=150)
    number: str | None = Field(default=None, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    neighborhood: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    zip_code: str | None = Field(default=None, max_length=9)

    @field_validator("document", "phone", "zip_code", mode="before")
    @classmethod
    def normalize_numeric_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return digits_only(value)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Nome do cliente é obrigatório")

        return normalized

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip().upper()


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_type: CustomerType | None = None
    document_type: DocumentType | None = None
    document: str | None = Field(
        default=None,
        min_length=11,
        max_length=18,
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    street: str | None = Field(default=None, max_length=150)
    number: str | None = Field(default=None, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    neighborhood: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    zip_code: str | None = Field(default=None, max_length=9)

    @field_validator("document", "phone", "zip_code", mode="before")
    @classmethod
    def normalize_numeric_fields(
        cls,
        value: str | None,
    ) -> str | None:
        return digits_only(value)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError("Nome do cliente é obrigatório")

        return normalized

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip().upper()


class CustomerStatusUpdate(BaseModel):
    is_active: bool


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 4: Verificar dependência de e-mail**

Rodar:

```powershell
python -c "import email_validator; print('email-validator OK')"
```

Esperado: `email-validator OK`.

Se ocorrer `ModuleNotFoundError`, instalar e registrar a dependência conforme o arquivo usado pelo projeto:

```powershell
pip install email-validator
```

Adicionar `email-validator` ao arquivo de dependências do backend, mantendo o padrão já existente no projeto.

- [ ] **Step 5: Rodar os testes**

```powershell
python -m pytest tests\test_customer_schemas.py -v
```

Esperado: 3 testes passando.

- [ ] **Step 6: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\modules\customers\customer_schemas.py backend\tests\test_customer_schemas.py
git commit -m "feat: adiciona schemas de clientes"
```

---

### Task 3: Validação de CPF e CNPJ

**Files:**
- Create: `backend/app/modules/customers/document_validator.py`
- Test: `backend/tests/test_customer_document_validator.py`

**Interfaces:**
- Produces:
  - `is_valid_cpf(document: str) -> bool`
  - `is_valid_cnpj(document: str) -> bool`
  - `validate_document(document_type: DocumentType, document: str) -> bool`

- [ ] **Step 1: Criar testes de documento**

Criar `backend/tests/test_customer_document_validator.py`:

```python
from app.modules.customers.customer_model import DocumentType
from app.modules.customers.document_validator import (
    is_valid_cnpj,
    is_valid_cpf,
    validate_document,
)


def test_accepts_valid_cpf() -> None:
    assert is_valid_cpf("52998224725") is True


def test_rejects_invalid_cpf() -> None:
    assert is_valid_cpf("11111111111") is False
    assert is_valid_cpf("52998224724") is False


def test_accepts_valid_cnpj() -> None:
    assert is_valid_cnpj("11222333000181") is True


def test_rejects_invalid_cnpj() -> None:
    assert is_valid_cnpj("11111111111111") is False
    assert is_valid_cnpj("11222333000180") is False


def test_dispatches_validation_by_document_type() -> None:
    assert validate_document(
        DocumentType.CPF,
        "52998224725",
    ) is True

    assert validate_document(
        DocumentType.CNPJ,
        "11222333000181",
    ) is True
```

- [ ] **Step 2: Rodar e confirmar falha**

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_customer_document_validator.py -v
```

Esperado: erro de importação.

- [ ] **Step 3: Implementar o validador**

Criar `backend/app/modules/customers/document_validator.py`:

```python
from app.modules.customers.customer_model import DocumentType


def _calculate_digit(
    digits: list[int],
    weights: list[int],
) -> int:
    total = sum(
        digit * weight
        for digit, weight in zip(digits, weights, strict=True)
    )

    remainder = total % 11

    return 0 if remainder < 2 else 11 - remainder


def is_valid_cpf(document: str) -> bool:
    if len(document) != 11:
        return False

    if document == document[0] * 11:
        return False

    if not document.isdigit():
        return False

    digits = [int(value) for value in document]

    first_digit = _calculate_digit(
        digits[:9],
        list(range(10, 1, -1)),
    )

    second_digit = _calculate_digit(
        digits[:9] + [first_digit],
        list(range(11, 1, -1)),
    )

    return digits[-2:] == [
        first_digit,
        second_digit,
    ]


def is_valid_cnpj(document: str) -> bool:
    if len(document) != 14:
        return False

    if document == document[0] * 14:
        return False

    if not document.isdigit():
        return False

    digits = [int(value) for value in document]

    first_digit = _calculate_digit(
        digits[:12],
        [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
    )

    second_digit = _calculate_digit(
        digits[:12] + [first_digit],
        [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
    )

    return digits[-2:] == [
        first_digit,
        second_digit,
    ]


def validate_document(
    document_type: DocumentType,
    document: str,
) -> bool:
    if document_type == DocumentType.CPF:
        return is_valid_cpf(document)

    return is_valid_cnpj(document)
```

- [ ] **Step 4: Rodar os testes**

```powershell
python -m pytest tests\test_customer_document_validator.py -v
```

Esperado: 5 testes passando.

- [ ] **Step 5: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\modules\customers\document_validator.py backend\tests\test_customer_document_validator.py
git commit -m "feat: adiciona validacao de CPF e CNPJ"
```

---

### Task 4: Repository e service de clientes

**Files:**
- Create: `backend/app/modules/customers/customer_repository.py`
- Create: `backend/app/modules/customers/customer_service.py`
- Test: `backend/tests/test_customer_service.py`

**Interfaces:**
- Produces:
  - `CustomerRepository`
  - `CustomerNotFoundError`
  - `CustomerDocumentAlreadyExistsError`
  - `InvalidCustomerDocumentError`
  - `CustomerService`

- [ ] **Step 1: Criar testes do service**

Criar `backend/tests/test_customer_service.py`:

```python
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.customers.customer_model import (
    Customer,
    CustomerType,
    DocumentType,
)
from app.modules.customers.customer_schemas import (
    CustomerCreate,
)
from app.modules.customers.customer_service import (
    CustomerDocumentAlreadyExistsError,
    CustomerService,
    InvalidCustomerDocumentError,
)


@pytest.mark.asyncio
async def test_service_creates_valid_customer() -> None:
    repository = MagicMock()
    repository.get_by_document = AsyncMock(return_value=None)

    created_customer = Customer(
        id=uuid4(),
        customer_type=CustomerType.INDIVIDUAL,
        document_type=DocumentType.CPF,
        document="52998224725",
        name="Cliente Teste",
        is_active=True,
    )

    repository.create = AsyncMock(
        return_value=created_customer
    )

    service = CustomerService(repository)

    result = await service.create(
        CustomerCreate(
            customer_type=CustomerType.INDIVIDUAL,
            document_type=DocumentType.CPF,
            document="529.982.247-25",
            name="Cliente Teste",
        )
    )

    assert result.document == "52998224725"
    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_service_rejects_invalid_document() -> None:
    service = CustomerService(MagicMock())

    with pytest.raises(InvalidCustomerDocumentError):
        await service.create(
            CustomerCreate(
                customer_type=CustomerType.INDIVIDUAL,
                document_type=DocumentType.CPF,
                document="11111111111",
                name="Cliente Inválido",
            )
        )


@pytest.mark.asyncio
async def test_service_rejects_duplicate_document() -> None:
    repository = MagicMock()
    repository.get_by_document = AsyncMock(
        return_value=MagicMock()
    )

    service = CustomerService(repository)

    with pytest.raises(
        CustomerDocumentAlreadyExistsError
    ):
        await service.create(
            CustomerCreate(
                customer_type=CustomerType.COMPANY,
                document_type=DocumentType.CNPJ,
                document="11222333000181",
                name="Empresa Duplicada",
            )
        )
```

- [ ] **Step 2: Rodar e confirmar falha**

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_customer_service.py -v
```

Esperado: erro de importação.

- [ ] **Step 3: Implementar o repository**

Criar `backend/app/modules/customers/customer_repository.py`:

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.customer_model import Customer
from app.modules.customers.customer_schemas import (
    CustomerCreate,
    CustomerUpdate,
)


class CustomerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        customer_id: UUID,
    ) -> Customer | None:
        return await self.session.get(Customer, customer_id)

    async def get_by_document(
        self,
        document: str,
    ) -> Customer | None:
        statement = select(Customer).where(
            Customer.document == document
        )

        return await self.session.scalar(statement)

    async def list_all(
        self,
        include_inactive: bool = False,
    ) -> list[Customer]:
        statement = select(Customer)

        if not include_inactive:
            statement = statement.where(
                Customer.is_active.is_(True)
            )

        statement = statement.order_by(Customer.name.asc())

        result = await self.session.scalars(statement)

        return list(result.all())

    async def create(
        self,
        data: CustomerCreate,
    ) -> Customer:
        customer = Customer(**data.model_dump())

        self.session.add(customer)
        await self.session.commit()
        await self.session.refresh(customer)

        return customer

    async def update(
        self,
        customer: Customer,
        data: CustomerUpdate,
    ) -> Customer:
        for field, value in data.model_dump(
            exclude_unset=True
        ).items():
            setattr(customer, field, value)

        await self.session.commit()
        await self.session.refresh(customer)

        return customer

    async def set_active(
        self,
        customer: Customer,
        is_active: bool,
    ) -> Customer:
        customer.is_active = is_active

        await self.session.commit()
        await self.session.refresh(customer)

        return customer
```

- [ ] **Step 4: Implementar o service**

Criar `backend/app/modules/customers/customer_service.py`:

```python
from uuid import UUID

from app.modules.customers.customer_model import Customer
from app.modules.customers.customer_repository import (
    CustomerRepository,
)
from app.modules.customers.customer_schemas import (
    CustomerCreate,
    CustomerUpdate,
)
from app.modules.customers.document_validator import (
    validate_document,
)


class CustomerNotFoundError(Exception):
    pass


class CustomerDocumentAlreadyExistsError(Exception):
    pass


class InvalidCustomerDocumentError(Exception):
    pass


class CustomerService:
    def __init__(
        self,
        repository: CustomerRepository,
    ) -> None:
        self.repository = repository

    def _validate_document(
        self,
        document_type,
        document: str,
    ) -> None:
        if not validate_document(
            document_type,
            document,
        ):
            raise InvalidCustomerDocumentError(
                "CPF ou CNPJ inválido"
            )

    async def create(
        self,
        data: CustomerCreate,
    ) -> Customer:
        self._validate_document(
            data.document_type,
            data.document,
        )

        existing = await self.repository.get_by_document(
            data.document
        )

        if existing is not None:
            raise CustomerDocumentAlreadyExistsError(
                "Já existe um cliente com esse documento"
            )

        return await self.repository.create(data)

    async def update(
        self,
        customer_id: UUID,
        data: CustomerUpdate,
    ) -> Customer:
        customer = await self.repository.get_by_id(
            customer_id
        )

        if customer is None:
            raise CustomerNotFoundError(
                "Cliente não encontrado"
            )

        document_type = (
            data.document_type
            if data.document_type is not None
            else customer.document_type
        )

        document = (
            data.document
            if data.document is not None
            else customer.document
        )

        self._validate_document(
            document_type,
            document,
        )

        if document != customer.document:
            existing = await self.repository.get_by_document(
                document
            )

            if existing is not None:
                raise CustomerDocumentAlreadyExistsError(
                    "Já existe um cliente com esse documento"
                )

        return await self.repository.update(
            customer,
            data,
        )

    async def set_active(
        self,
        customer_id: UUID,
        is_active: bool,
    ) -> Customer:
        customer = await self.repository.get_by_id(
            customer_id
        )

        if customer is None:
            raise CustomerNotFoundError(
                "Cliente não encontrado"
            )

        return await self.repository.set_active(
            customer,
            is_active,
        )
```

- [ ] **Step 5: Rodar os testes**

```powershell
python -m pytest tests\test_customer_service.py -v
```

Esperado: 3 testes passando.

- [ ] **Step 6: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\modules\customers\customer_repository.py backend\app\modules\customers\customer_service.py backend\tests\test_customer_service.py
git commit -m "feat: adiciona servico de clientes"
```

---

### Task 5: Migração da tabela customers

**Files:**
- Create: `backend/app/migrations/versions/0007_create_customers.py`
- Test: `backend/tests/test_customer_migration.py`

**Interfaces:**
- Produces tabela PostgreSQL `customers`.

- [ ] **Step 1: Criar teste da migração**

Criar `backend/tests/test_customer_migration.py`:

```python
from pathlib import Path


def test_customer_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0007_create_customers.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"customers"' in content
    assert "customer_type" in content
    assert "customer_document_type" in content
    assert "document" in content
    assert "is_active" in content
```

- [ ] **Step 2: Rodar e confirmar falha**

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_customer_migration.py -v
```

Esperado: falha porque o arquivo não existe.

- [ ] **Step 3: Implementar a migração**

Criar `backend/app/migrations/versions/0007_create_customers.py`:

```python
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

customer_type = postgresql.ENUM(
    "INDIVIDUAL",
    "COMPANY",
    name="customer_type",
    create_type=False,
)

customer_document_type = postgresql.ENUM(
    "CPF",
    "CNPJ",
    name="customer_document_type",
    create_type=False,
)


def upgrade() -> None:
    customer_type.create(
        op.get_bind(),
        checkfirst=True,
    )

    customer_document_type.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "customer_type",
            customer_type,
            nullable=False,
        ),
        sa.Column(
            "document_type",
            customer_document_type,
            nullable=False,
        ),
        sa.Column(
            "document",
            sa.String(length=14),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "phone",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column(
            "email",
            sa.String(length=254),
            nullable=True,
        ),
        sa.Column(
            "street",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "number",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column(
            "complement",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "neighborhood",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "city",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "state",
            sa.String(length=2),
            nullable=True,
        ),
        sa.Column(
            "zip_code",
            sa.String(length=8),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "document",
            name="uq_customers_document",
        ),
    )

    op.create_index(
        op.f("ix_customers_document"),
        "customers",
        ["document"],
        unique=True,
    )

    op.create_index(
        op.f("ix_customers_name"),
        "customers",
        ["name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_customers_name"),
        table_name="customers",
    )

    op.drop_index(
        op.f("ix_customers_document"),
        table_name="customers",
    )

    op.drop_table("customers")

    customer_document_type.drop(
        op.get_bind(),
        checkfirst=True,
    )

    customer_type.drop(
        op.get_bind(),
        checkfirst=True,
    )
```

- [ ] **Step 4: Rodar os testes**

```powershell
python -m pytest tests\test_customer_migration.py -v
```

Esperado: 1 teste passando.

- [ ] **Step 5: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\migrations\versions\0007_create_customers.py backend\tests\test_customer_migration.py
git commit -m "feat: adiciona migracao de clientes"
```

---

### Task 6: API de clientes e permissões

**Files:**
- Modify: `backend/app/api/dependencies.py`
- Create: `backend/app/api/routers/customers.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_customers_api.py`

**Interfaces:**
- Produces:
  - `GET /api/v1/customers`
  - `GET /api/v1/customers/{customer_id}`
  - `POST /api/v1/customers`
  - `PATCH /api/v1/customers/{customer_id}`
  - `PATCH /api/v1/customers/{customer_id}/status`

- [ ] **Step 1: Criar testes da API**

Criar `backend/tests/test_customers_api.py`:

```python
from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.dependencies import (
    get_current_user,
    get_customer_repository,
)
from app.core.enums import UserRole
from app.main import app
from app.modules.customers.customer_model import Customer
from app.modules.users.model import User


def make_user(role: UserRole) -> User:
    return User(
        id=uuid4(),
        name="Usuário",
        email=f"{role.value.lower()}@agrosales.com",
        password_hash="hash",
        role=role,
        is_active=True,
    )


def test_vendor_cannot_inactivate_customer(client) -> None:
    customer_id = uuid4()

    repository = AsyncMock()
    repository.get_by_id.return_value = Customer(
        id=customer_id,
        customer_type="INDIVIDUAL",
        document_type="CPF",
        document="52998224725",
        name="Cliente Teste",
        is_active=True,
    )

    app.dependency_overrides[get_current_user] = lambda: make_user(
        UserRole.VENDEDOR
    )
    app.dependency_overrides[get_customer_repository] = (
        lambda: repository
    )

    response = client.patch(
        f"/api/v1/customers/{customer_id}/status",
        json={"is_active": False},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 403


def test_rejects_invalid_customer_document(client) -> None:
    repository = AsyncMock()

    app.dependency_overrides[get_current_user] = lambda: make_user(
        UserRole.PRODUTOR
    )
    app.dependency_overrides[get_customer_repository] = (
        lambda: repository
    )

    response = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "document_type": "CPF",
            "document": "111.111.111-11",
            "name": "Cliente Inválido",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["detail"] == "CPF ou CNPJ inválido"
```

- [ ] **Step 2: Rodar e confirmar falha**

```powershell
cd "C:\Projetos\agrosales\backend"
python -m pytest tests\test_customers_api.py -v
```

Esperado: erro de importação ou rota não encontrada.

- [ ] **Step 3: Adicionar a dependência**

Em `backend/app/api/dependencies.py`, adicionar:

```python
from app.modules.customers.customer_repository import (
    CustomerRepository,
)
```

E:

```python
def get_customer_repository(
    session: SessionDependency,
) -> CustomerRepository:
    return CustomerRepository(session)
```

- [ ] **Step 4: Criar o router**

Criar `backend/app/api/routers/customers.py`:

```python
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_customer_repository,
    require_roles,
)
from app.core.enums import UserRole
from app.modules.customers.customer_model import Customer
from app.modules.customers.customer_repository import (
    CustomerRepository,
)
from app.modules.customers.customer_schemas import (
    CustomerCreate,
    CustomerRead,
    CustomerStatusUpdate,
    CustomerUpdate,
)
from app.modules.customers.customer_service import (
    CustomerDocumentAlreadyExistsError,
    CustomerNotFoundError,
    CustomerService,
    InvalidCustomerDocumentError,
)
from app.modules.users.model import User

router = APIRouter(
    prefix="/customers",
    tags=["Clientes"],
)


def build_service(
    repository: CustomerRepository,
) -> CustomerService:
    return CustomerService(repository)


def raise_customer_error(error: Exception) -> None:
    if isinstance(error, CustomerNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    if isinstance(
        error,
        CustomerDocumentAlreadyExistsError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if isinstance(error, InvalidCustomerDocumentError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    raise error


@router.get(
    "",
    response_model=list[CustomerRead],
)
async def list_customers(
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
    include_inactive: bool = Query(default=False),
) -> list[Customer]:
    return await repository.list_all(include_inactive)


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
)
async def get_customer(
    customer_id: UUID,
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> Customer:
    customer = await repository.get_by_id(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado",
        )

    return customer


@router.post(
    "",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    data: CustomerCreate,
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> Customer:
    try:
        return await build_service(repository).create(data)
    except Exception as error:
        raise_customer_error(error)
        raise


@router.patch(
    "/{customer_id}",
    response_model=CustomerRead,
)
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
                UserRole.VENDEDOR,
            )
        ),
    ],
) -> Customer:
    try:
        return await build_service(repository).update(
            customer_id,
            data,
        )
    except Exception as error:
        raise_customer_error(error)
        raise


@router.patch(
    "/{customer_id}/status",
    response_model=CustomerRead,
)
async def update_customer_status(
    customer_id: UUID,
    data: CustomerStatusUpdate,
    repository: Annotated[
        CustomerRepository,
        Depends(get_customer_repository),
    ],
    _: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.ADMINISTRADOR,
                UserRole.PRODUTOR,
            )
        ),
    ],
) -> Customer:
    try:
        return await build_service(repository).set_active(
            customer_id,
            data.is_active,
        )
    except Exception as error:
        raise_customer_error(error)
        raise
```

- [ ] **Step 5: Registrar o router**

Em `backend/app/main.py`, adicionar:

```python
from app.api.routers.customers import (
    router as customers_router,
)
```

E:

```python
app.include_router(
    customers_router,
    prefix=settings.api_v1_prefix,
)
```

- [ ] **Step 6: Rodar os testes da API**

```powershell
python -m pytest tests\test_customers_api.py -v
```

Esperado: 2 testes passando.

- [ ] **Step 7: Rodar toda a suíte**

```powershell
python -m pytest -v
```

Esperado: todos os testes passando.

- [ ] **Step 8: Commit**

```powershell
cd "C:\Projetos\agrosales"
git add backend\app\api\dependencies.py backend\app\api\routers\customers.py backend\app\main.py backend\tests\test_customers_api.py
git commit -m "feat: adiciona API de clientes"
```

---

### Task 7: Aplicar no Docker e validar

**Files:**
- Verify: módulo de clientes completo.

- [ ] **Step 1: Rebuild e migração**

No notebook com Docker:

```powershell
cd "\\192.168.100.37\Projetos\agrosales"
docker compose up -d --build api
docker compose exec api alembic upgrade head
docker compose exec api alembic current
```

Esperado:

```text
0007 (head)
```

- [ ] **Step 2: Confirmar a tabela**

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "\d customers"
```

Esperado: tabela com documento único, tipos, endereço e status.

- [ ] **Step 3: Validar no Swagger**

No PC principal:

```text
http://192.168.100.30:8000/docs
```

Criar pessoa física:

```json
{
  "customer_type": "INDIVIDUAL",
  "document_type": "CPF",
  "document": "529.982.247-25",
  "name": "Cliente Teste",
  "phone": "(67) 99999-9999",
  "email": "cliente@exemplo.com",
  "street": "Rua das Flores",
  "number": "100",
  "complement": null,
  "neighborhood": "Centro",
  "city": "Campo Grande",
  "state": "MS",
  "zip_code": "79000-000"
}
```

Esperado: `201 Created`.

- [ ] **Step 4: Conferir no PostgreSQL**

No notebook com Docker:

```powershell
docker compose exec db psql -U agrosales -d agrosales -c "SELECT id, customer_type, document_type, document, name, is_active FROM customers ORDER BY created_at DESC;"
```

Esperado: cliente persistido com documento sem pontuação.

- [ ] **Step 5: Push final**

No PC principal:

```powershell
cd "C:\Projetos\agrosales"
git push
```
