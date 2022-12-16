import gradio as gr
import os
import requests


DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"


def read_mol(molpath):
    with open(molpath, "r") as fp:
        lines = fp.readlines()
    mol = ""
    for l in lines:
        mol += l
    return mol


def molecule(input_pdb):
    mol = read_mol(input_pdb)

    x = (
        """<!DOCTYPE html>
        <html>
        <head>    
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <style>
    body{
        font-family:sans-serif
    }
    .mol-container {
    width: 100%;
    height: 380px;
    position: relative;
    }
    .mol-container select{
        background-image:None;
    }
    </style>
    <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
    </head>
    <body style="overflow: hidden;">  
    <div id="container" class="mol-container"></div>
  
            <script>
               let pdb = `"""
        + mol
        + """`  
      
             $(document).ready(function () {
                let element = $("#container");
                let config = { backgroundColor: "white" };
                let viewer = $3Dmol.createViewer(element, config);
                let colorAlpha = function (atom) {
                    if (atom.b < 0.5) {
                        return "OrangeRed";
                    } else if (atom.b < 0.7) {
                        return "Gold";
                    } else if (atom.b < 0.9) {
                        return "MediumTurquoise";
                    } else {
                        return "Blue";
                    }
                };
                
                viewer.addModel(pdb, "pdb");
                // set plddt coloring
                viewer.getModel(0).setStyle({cartoon: { colorfunc: colorAlpha }});
                // display pLDDT tooltips when hovering over atoms
                viewer.getModel(0).setHoverable({}, true,
                        function (atom, viewer, event, container) {
                            if (!atom.label) {
                                atom.label = viewer.addLabel(atom.resn + atom.resi + " pLDDT=" + atom.b, { position: atom, backgroundColor: "mintcream", fontColor: "black" });
                            }
                        },
                        function (atom, viewer) {
                            if (atom.label) {
                                viewer.removeLabel(atom.label);
                                delete atom.label;
                            }
                        }
                    );
                viewer.zoomTo();
                viewer.render();
                viewer.zoom(1.2, 2000);
              })
        </script>
        </body></html>"""
    )

    return f"""<iframe style="width: 100%; height: 380px" name="result" allow="midi; geolocation; microphone; camera; 
    display-capture; encrypted-media;" sandbox="allow-modals allow-forms 
    allow-scripts allow-same-origin allow-popups 
    allow-top-navigation-by-user-activation allow-downloads" allowfullscreen="" 
    allowpaymentrequest="" frameborder="0" srcdoc='{x}'></iframe>"""

import tempfile


def update(sequence=DEFAULT_SEQ):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence)
    name = sequence[:3] + sequence[-3:] 
    pdb_string = response.content.decode('utf-8')
    
    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, "w") as f:
        f.write(pdb_string)
    print("File name", tmp.name)
    return molecule(tmp.name)


def suggest(option):
   if option == "Plastic degradation protein":
     suggestion = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
   elif option == "Antifreeze protein":
     suggestion = "QCTGGADCTSCTGACTGCGNCPNAVTCTNSQHCVKANTCTGSTDCNTAQTCTNSKDCFEANTCTDSTNCYKATACTNSSGCPGH"
   elif option == "AI Generated protein":
     suggestion = "MSGMKKLYEYTVTTLDEFLEKLKEFILNTSKDKIYKLTITNPKLIKDIGKAIAKAAEIADVDPKEIEEMIKAVEENELTKLVITIEQTDDKYVIKVELENEDGLVHSFEIYFKNKEEMEKFLELLEKLISKLSGS"
   elif option == "7-bladed propeller fold":
     suggestion = "VKLAGNSSLCPINGWAVYSKDNSIRIGSKGDVFVIREPFISCSHLECRTFFLTQGALLNDKHSNGTVKDRSPHRTLMSCPVGEAPSPYNSRFESVAWSASACHDGTSWLTIGISGPDNGAVAVLKYNGIITDTIKSWRNNILRTQESECACVNGSCFTVMTDGPSNGQASYKIFKMEKGKVVKSVELDAPNYHYEECSCYPNAGEITCVCRDNWHGSNRPWVSFNQNLEYQIGYICSGVFGDNPRPNDGTGSCGPVSSNGAYGVKGFSFKYGNGVWIGRTKSTNSRSGFEMIWDPNGWTETDSSFSVKQDIVAITDWSGYSGSFVQHPELTGLDCIRPCFWVELIRGRPKESTIWTSGSSISFCGVNSDTVGWSWPDGAELPFTIDK"
   else:
     suggestion = ""
   return suggestion


demo = gr.Blocks()


with demo:
    gr.HTML("""<div style="text-align: center; max-width: 700px; margin: 0 auto;">
              <div
              style="
                  display: inline-flex;
                  align-items: center;
                  gap: 0.8rem;
                  font-size: 1.75rem;
              "
              >
              <h1 style="font-weight: 900; margin-bottom: 7px; margin-top: 5px;">
                   ESMFold Protein Folding demo
              </h1>
              </div>
              <p style="margin-bottom: 10px; font-size: 94%">
                  You can input a single protein sequence and you get the predicted protein structure
              </p>
          </div>""")
    name = gr.Dropdown(label="Choose a Sample Protein", value="Plastic degradation protein", choices=["Antifreeze protein", "Plastic degradation protein",  "AI Generated protein", "7-bladed propeller fold", "custom"])
    with gr.Row():
        inp = gr.Textbox(label="Protein sequence", lines=3, value=DEFAULT_SEQ, placeholder="Write your protein sequence here...")
        btn = gr.Button("🔬 Predict Structure ").style(full_width=False)
    mol = gr.HTML(update)    
    #download = gr.File(label="Download file")
    btn.click(fn=update, inputs=inp, outputs=mol)
    
    name.change(fn=suggest, inputs=name, outputs=inp)
    name.change(fn=lambda :"", inputs=None, outputs=mol)
    inp.change(fn=update, inputs=inp, outputs=mol)
    
    gr.Markdown("A demo of [ESM](https://esmatlas.com/about) by Meta using the API. You can also use ESM in Hugging Face `transformers` as shown [here](https://github.com/huggingface/notebooks/blob/ab81a52182acf691e6743a50bc47bd1c1622086f/examples/protein_folding.ipynb), which is supported since [v4.24](https://github.com/huggingface/transformers/releases/tag/v4.24.0).")
demo.launch(debug=True)