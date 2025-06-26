# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.tenv
    pkgs.docker
    pkgs.python312
    pkgs.python312Packages.pip
  ];
  services.docker.enable = true;
  
  # Load environment variables from .env
  env = {};

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
    ];
    # env = pkgs.dotenv.load ./.env.PROD.local; # Load variables here
    # Enable previews
    previews = {
      enable = true;
      previews = {
        # web = {
        #   # Example: run "npm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
        #   command = ["npm" "run" "dev"];
        #   manager = "web";
        #   env = {
        #     # Environment variables to set for your server
        #     PORT = "$PORT";
        #   };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {};
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # watch-backend = "npm run watch-backend";
        # pip install -r test/requirements.txt
        create-venv = ''
          python -m venv .venv
          source .venv/bin/activate
          pip install -r src/surquest/GCP/requirements.txt
          pip install -r test/surquest/GCP/requirements.txt
        '';
        set-credentials = ''
          gcloud auth application-default login --impersonate-service-account="adm--deployer@analytics-data-mart.iam.gserviceaccount.com"
          cp /home/user/.config/gcloud/application_default_credentials.json ./credentials/PROD/sa.keyfile.json
        '';
      };
    };
  };
}