{% from "partials/model-class" import modelClass -%}
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Sequence

from dataclasses_json import LetterCase, dataclass_json

{%- set imports = schema | getImports -%}
{{ imports }}

{{ modelClass(schemaName, schema.properties(), schema.required(), 0 ) }}
