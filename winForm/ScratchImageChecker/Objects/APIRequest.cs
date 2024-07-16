using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ScratchImageChecker.Objects
{
    public class APIRequest
    {

        public APIRequest(string text, int selectedIndex)
        {
            this.Address = text;
            this.Label = selectedIndex.ToString();
        }

        public string Address { get; set; }
        public string Label { get; set; }
    }
}
