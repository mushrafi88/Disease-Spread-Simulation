{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = { self, nixpkgs, devenv, systems, nixpkgs-python, ... } @ inputs:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      packages = forEachSystem (system: {
        devenv-up = self.devShells.${system}.default.config.procfileScript;
      });

      devShells = forEachSystem
        (system:
          let
            pkgs = nixpkgs.legacyPackages.${system};
          in
          {
            default = devenv.lib.mkShell {
              inherit inputs pkgs;
              modules = [
                {
                  # https://devenv.sh/reference/options/
                  packages = [
                   pkgs.stdenv.cc 
                   pkgs.gnumake
                   pkgs.glib 
                   pkgs.glibc
                   pkgs.python311Packages.imageio
                   pkgs.python311Packages.numpy 
                   pkgs.python311Packages.pandas 
                   pkgs.python311Packages.seaborn 
                   pkgs.python311Packages.networkx 
                   pkgs.python311Packages.pillow
                   pkgs.python311Packages.pyparsing
                   pkgs.python311Packages.packaging
                   pkgs.python311Packages.kiwisolver
                   pkgs.python311Packages.fonttools
                   pkgs.python311Packages.cycler
                   pkgs.python311Packages.contourpy
                   pkgs.python311Packages.matplotlib
                   pkgs.python311Packages.tqdm
                  ]; # XXX pkgs?

                  languages.python = {
                    enable = true;
                    version = "3.11.3";
                    venv = {
                      enable = true;
                      quiet = true;
                    };
                      };
                  env.LD_LIBRARY_PATH = "${nixpkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib ]}:/run/opengl-driver/lib/:${nixpkgs.lib.makeLibraryPath [ pkgs.glib ]}";
                  enterShell = ''
                  pip install mesa==1.2.1 streamlit
                  '';
                  processes.myapp.exec = "streamlit run app_streamlit.py";
                }
              ];
            };
          });
    };
}
