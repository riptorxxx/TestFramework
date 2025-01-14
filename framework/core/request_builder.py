from dataclasses import asdict, fields
from typing import Dict, Any


class APIRequestBuilder:
    @staticmethod
    def build(data_object: Any, mapping: Dict[str, str] = None) -> dict:
        # Получить только общедоступные поля из класса данных
        public_fields = {field.name: getattr(data_object, field.name)
                         for field in fields(data_object)
                         if not field.name.startswith('_')}

        result = {}
        if mapping:
            for src_field, api_field in mapping.items():
                if src_field in public_fields and public_fields[src_field] is not None:
                    result[api_field] = public_fields[src_field]
        else:
            result = {k: v for k, v in public_fields.items() if v is not None}

        return result

# class APIRequestBuilder:
#     @staticmethod
#     def build(data_object: Any, mapping: Dict[str, str] = None) -> dict:
#         base_dict = asdict(data_object)
#         result = {}
#         if mapping:
#             for src_field, api_field in mapping.items():
#                 if src_field in base_dict and base_dict[src_field] is not None:
#                     result[api_field] = base_dict[src_field]
#         else:
#             result = {k: v for k, v in base_dict.items() if v is not None}
#         return result
