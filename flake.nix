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
                   pkgs.streamlit
                   pkgs.python311Packages.imageio
                   pkgs.python311Packages.zipp
                   pkgs.python311Packages.jsonschema
                   pkgs.python311Packages.toolz
                   pkgs.python311Packages.altair
                   pkgs.python311Packages.blinker
                   pkgs.python311Packages.cachetools
                   pkgs.python311Packages.gitpython
                   pkgs.python311Packages.protobuf
                   pkgs.python311Packages.pyarrow
                   pkgs.python311Packages.pydeck
                   pkgs.python311Packages.tenacity
                   pkgs.python311Packages.toml 
                   pkgs.python311Packages.tzlocal
                   pkgs.python311Packages.watchdog
                   pkgs.python311Packages.validators
                   pkgs.python311Packages.typing-extensions 
                   pkgs.python311Packages.importlib-metadata
                   pkgs.python311Packages.streamlit
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

                  enterShell = ''pip install mesa==1.2.1'';

                  #processes.myapp.exec = "";
                }
              ];
            };
          });
    };
}
