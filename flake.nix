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
          
          # Use a persistent directory to cache the venv and avoid re-installation
          CACHE_DIR="$HOME/.cache/spacy-viz"
          mkdir -p "$CACHE_DIR"
          
          # Update source files
          # We remove the old src directory to ensure deleted files are removed
          rm -rf "$CACHE_DIR/src"
          
          # Copy project files from the nix store to the cache directory
          cp -r ${self}/src "$CACHE_DIR/"
          cp -f ${self}/pyproject.toml "$CACHE_DIR/"
          
          if [ -f "${self}/README.md" ]; then
            cp -f ${self}/README.md "$CACHE_DIR/"
          else
            touch "$CACHE_DIR/README.md"
          fi
          
          if [ -f "${self}/uv.lock" ]; then
            cp -f ${self}/uv.lock "$CACHE_DIR/"
          fi
          
          # Ensure the cache directory and files are writable
          chmod -R +w "$CACHE_DIR"
          
          cd "$CACHE_DIR"
          
          # Run the visualizer using uv in quiet mode (-q)
          # This reuses the .venv if it exists and matches the lockfile
          uv run -q python -m src.scripts.main "$@"
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