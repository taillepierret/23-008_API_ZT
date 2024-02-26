using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using HtmlAgilityPack;
using System.Diagnostics;

namespace LienTelechargement
{
    internal class Tools
    {
        public static string open_link(string url)
        {
            string contenu = "";
            try
            {
                using (HttpClient client = new HttpClient())
                {
                    HtmlWeb web = new HtmlWeb();
                    HtmlDocument document = web.Load(url);
                    contenu = document.DocumentNode.OuterHtml;
                    Debug.WriteLine(contenu);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erreur : {ex.Message}");
            }
            return contenu;
        }
    }
}
