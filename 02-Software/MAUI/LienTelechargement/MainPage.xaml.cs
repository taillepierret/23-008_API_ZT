namespace LienTelechargement;
using System.Diagnostics;

public partial class MainPage : ContentPage
{
	int count = 0;

	public MainPage()
	{
		InitializeComponent();
    }

    private void OnCounterClicked(object sender, EventArgs e)
    {
        count++;

        if (count == 1)
            CounterBtn.Text = $"Clicked {count} time";
        else
            CounterBtn.Text = $"Clicked {count} times";

        SemanticScreenReader.Announce(CounterBtn.Text);
        Debug.WriteLine("test");
        Tools.open_link("https://www.zone-telechargement.homes");

    }

    private void SearchBar_SearchButtonPressed(object sender, System.EventArgs e)
    {
        string searchTerm = searchBar.Text;
        Recherches.Text = searchTerm;
        // Ici, vous pouvez implémenter la logique de recherche en utilisant le terme "searchTerm"
        // et mettre à jour l'interface utilisateur en conséquence.
    }
}

