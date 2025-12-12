{
  description = "Spacy project environment with UV and System Dependencies";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        lib = pkgs.lib;
        
        # Define libraries needed for cairosvg/cairocffi
        extraLibs = with pkgs; [
          cairo
          pango
          gdk-pixbuf
          libffi
          gobject-introspection
          stdenv.cc.cc.lib
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python311
            uv
          ] ++ extraLibs;

          # Set LD_LIBRARY_PATH so python wheels (via cffi/ctypes) can find the shared libraries
          shellHook = ''
            export LD_LIBRARY_PATH=${lib.makeLibraryPath extraLibs}:$LD_LIBRARY_PATH
            
            echo "Environment loaded."
            echo "Python: $(python3 --version)"
            echo "UV: $(uv --version)"
            echo "To install/sync dependencies: uv sync"
            echo "To run the visualizer: uv run spacy-viz 'Your text here'"
          '';
        };

        apps.default = {
          type = "app";
          program = "${pkgs.writeShellScriptBin "spacy-viz" ''
            export LD_LIBRARY_PATH=${lib.makeLibraryPath extraLibs}:$LD_LIBRARY_PATH
            ${pkgs.uv}/bin/uv run spacy-viz "$@"
          ''}/bin/spacy-viz";
        };
      }
    );
}