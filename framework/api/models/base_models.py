from dataclasses import dataclass, asdict


@dataclass
class BaseConfig:
    def to_request(self) -> dict:
        # Get only non-None and non-internal fields
        data = {k: v for k, v in asdict(self).items()
                if not k.startswith('_') and v is not None}

        # Apply mapping if exists
        if hasattr(self, '_api_mapping'):
            return {self._api_mapping.get(k, k): v
                    for k, v in data.items()}
        return data

# @dataclass
# class BaseConfig:
#     _api_mapping: Dict[str, str] = field(default_factory=dict)
#
#     def to_request(self) -> dict:
#         return APIRequestBuilder.build(self, self._api_mapping)
