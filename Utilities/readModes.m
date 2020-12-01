% Title: Mode Shape Import
% Author: Brandon Crow
% Date: January 15, 2020

% This script is designed to import the mode shapes and plot the resulting
% mode shapes. After the data comes from Mystran, there are 4 data files
% corresponding to 4 modes of vibration.

clear, clc
close all;

% Set up loop to read the modes. The first path is for the AGARD wing and the
% second path is for the uCRM wing
%mainString = '/home/bcrow/Documents/Crow_CRM_Flutter/Github/ISGC_Research/AGARD/AeroelasticModal_FUN3D/aeroelastic_body1_mode';
mainString = '/home/bcrow/Documents/Crow_CRM_Flutter/Github/ISGC_Research/uCRM/Modal_Sims/Aeroelastic_fun3d/aeroelastic_body1_mode';

% currently, this array needs to be a 7 by x array where x is the line
% number of the last node
array = zeros(7,58218); %this number needs changing based on the first tessellation parameter in the .csm file
c = zeros(length(array(1,:)),1);

for modes = 1:4
    fileNumber = num2str(modes);
    fileID = fopen([mainString,fileNumber,'.dat']);

    % Import modal displacements from data file
    for i = 1:length(array(1,:))
        line = fgetl(fileID);
        if i > 4
            array(:,i-3) = str2num(line);
        end
    end

    fclose(fileID);


    % Map each displacement value to a color by mapping each displacement to a
    % corresponding value in the interval [1,10]
    maxDisplacement = max(array(7,:));
    multiplicationConstant = 10/(2*maxDisplacement+1);
    %C = multiplicationConstant*(array(7,:)+ maxDisplacement + 1);
    eta_max = 6; % for the uCRM eta_max = 6, AGARD eta_max = 0.002
    C = eta_max*array(7,:);


    % Plot x,y coordinates and z displacement
    figure
    scatter3(array(1,:),array(2,:),array(7,:),10,C,'filled')
    view(2)
    axis equal
    %xlim([-0.5,1.5]) % for the AGARD
    %ylim([-0.25,1]) % for the AGARD
    xlim([10,60]) % for the uCRM
    ylim([-2.5,40]) % for the uCRM
    %title(['AGARD Wing Mode ',fileNumber, ' Shapes'])
    xlabel('X [m]')
    ylabel('Y [m]')
    c = colorbar('location','southoutside','fontsize',20);
    c.Label.String = '\DeltaZ [m]';
    %caxis([-2*eta_max,3.5*eta_max]) % for the AGARD
    caxis([-0.04*eta_max,0.025*eta_max]) % for the uCRM
    set(gca,'FontSize',20)

end


%% Misc.

% I tried to use the contour command to make a plot of the modes, however I
% would need to make my Z vector a matrix corresponding to the x-y plane


%cn = ceil(max(array(7,:)));
%cm = colormap(jet(cn));
%c = linspace(-0.05,0.05,length(array(1,:)));
%colormap('jet')
