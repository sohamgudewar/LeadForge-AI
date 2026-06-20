from graph.workflow import graph

result = graph.invoke(
    {
        "company": "Slack"
    }
)

print(result)
