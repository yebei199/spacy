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

        # Define the executable package
        spacyVizPackage = pkgs.writeShellScriptBin "spacy-viz" ''
          export PATH=${pkgs.uv}/bin:${pkgs.python311}/bin:${pkgs.coreutils}/bin:$PATH
          export LD_LIBRARY_PATH=${lib.makeLibraryPath extraLibs}:$LD_LIBRARY_PATH
          
          # Create a temporary directory for execution
          WORK_DIR=$(mktemp -d)
          # Cleanup on exit
          trap "rm -rf $WORK_DIR" EXIT
          
          # Copy project files to the temporary directory
          # We copy from ${self} to ensure we have the source available at runtime
          cp -r ${self}/src $WORK_DIR/src
          cp ${self}/pyproject.toml $WORK_DIR/
          if [ -f "${self}/README.md" ]; then
            cp ${self}/README.md $WORK_DIR/
          else
            touch $WORK_DIR/README.md
          fi
          if [ -f "${self}/uv.lock" ]; then
            cp ${self}/uv.lock $WORK_DIR/
          fi
          
          # Make files writable so uv can update/delete them
          chmod -R +w $WORK_DIR
          
          cd $WORK_DIR
          
          # Run the visualizer using uv
          # We assume internet access or cached packages are available for uv
          uv run python -m src.scripts.main "$@"
        '';
      in
      {
        packages.default = spacyVizPackage;

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python311
            uv
          ] ++ extraLibs;

          shellHook = ''
            export LD_LIBRARY_PATH=${lib.makeLibraryPath extraLibs}:$LD_LIBRARY_PATH
            
            echo "Environment loaded."
            echo "Python: $(python3 --version)"
            echo "UV: $(uv --version)"
            echo "To install/sync dependencies: uv sync"
            echo "To run the visualizer: uv run python -m src.scripts.main 'Your text here'"
          '';
        };

        apps.default = {
          type = "app";
          program = "${spacyVizPackage}/bin/spacy-viz";
        };
      }
    );
}