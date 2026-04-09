import click

class CLI:
    def __init__(self):
        pass
    def run_single(self):
        pass

    

@click.command()
@click.argument("prompt", required=False)
def main(
    prompt: str | None
):
        
    print("Successful")
    
main()