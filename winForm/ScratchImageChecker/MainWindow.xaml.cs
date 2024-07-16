using Microsoft.Win32;
using Newtonsoft.Json;
using NLog;
using ScratchImageChecker.Objects;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace ScratchImageChecker
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        Logger logger = LogManager.GetCurrentClassLogger();
        public MainWindow()
        {
            InitializeComponent();
            showForm();
        }
        void showForm()
        {
            cmbScartchState.SelectedIndex = 0;
            btnCheck.IsEnabled = false;
        }
        private void btnExit_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
            logger.Info("Closed");
        }

        private async void btnCheck_Click(object sender, RoutedEventArgs e)
        {
            try
            {

                var client = new HttpClient();
                var request = new HttpRequestMessage(HttpMethod.Post, Properties.Settings.Default.UrlAddress);
                APIRequest aRequestBody = new APIRequest(txtAddress.Text,cmbScartchState.SelectedIndex);

                var content =JsonConvert.SerializeObject(aRequestBody);
                request.Content = new StringContent(content,null, "application/json");
                var response = await client.SendAsync(request);
                response.EnsureSuccessStatusCode();
                lblOutput.Content= await response.Content.ReadAsStringAsync();
            }
            catch(Exception ex)
            {
                logger.Error(ex);
                lblOutput.Content = ex.Message;
            }
        }

        private void btnPath_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog dlgOpenFile=new OpenFileDialog();
            dlgOpenFile.Filter = Properties.Settings.Default.OpenDialogeExtention;
            if (dlgOpenFile.ShowDialog()== true)
            {
                if (File.Exists(dlgOpenFile.FileName))
                {
                    imgMain.Source = new BitmapImage(new Uri(dlgOpenFile.FileName));
                    txtAddress.Text = dlgOpenFile.FileName;
                    btnCheck.IsEnabled = true;
                }
            }
        }
    }
}
