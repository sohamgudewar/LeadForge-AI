from graph.workflow import graph

result = graph.invoke(
    {
        "company": "Stripe"
    }
)

print(result)
