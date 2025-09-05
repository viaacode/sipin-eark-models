{
  description = "Nix flake for the prefect-flow-iiif-manifest-etl";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  inputs.nixpkgs-unstable.url = "nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs, nixpkgs-unstable }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
        pkgs-unstable = import nixpkgs-unstable { inherit system; };
      });
    in
    {
      devShells = forEachSupportedSystem ({ pkgs, pkgs-unstable }: {
        default = pkgs.mkShell {
          venvDir = ".venv";
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
          packages = with pkgs; [ 
            pyright
            python312
            libxml2
            ruff
          ] ++
            (with pkgs.python312Packages; [
              pip
              venvShellHook
            ]);
        };
      });
    };
}
