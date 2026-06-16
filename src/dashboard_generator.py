def generate_html_dashboard(summary_df, output_path):

    overall_score = round(
        summary_df["quality_score"].mean(), 2
    )

    html = f"""
    <html>
    <head>
        <title>Data Quality Dashboard</title>

        <style>

        body {{
            font-family: Arial;
            margin: 40px;
        }}

        table {{
            border-collapse: collapse;
            width: 70%;
        }}

        th, td {{
            border: 1px solid black;
            padding: 10px;
            text-align: center;
        }}

        th {{
            background-color: lightgray;
        }}

        </style>

    </head>

    <body>

        <h1>Data Quality Dashboard</h1>

        <h2>Overall Quality Score: {overall_score}%</h2>

        {summary_df.to_html(index=False)}

    </body>
    </html>
    """

    with open(output_path, "w") as file:
        file.write(html)