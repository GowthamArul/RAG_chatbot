from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import TextNode, NodeWithScore, QueryBundle


class DefaultNodePostProcessor(BaseNodePostprocessor):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def class_name(cls) -> str:
        return "DefaultNodePostProcessor"
    
    def _postprocess_nodes(self, 
                           nodes : list[NodeWithScore], 
                           query_bundle: QueryBundle | None = None,) -> list[NodeWithScore]:
        if len(nodes) == 0:
            default_node = NodeWithScore(
                node=TextNode(text="No relevant documents found."),
                score=0.0,
            )
            default_node.node.metadata.update({"is_default": True})
            return [default_node]

        return nodes
    