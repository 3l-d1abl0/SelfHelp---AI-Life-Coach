export const layoutConfig = {

	pagesWithoutProfile: [
		'/meeting',
		'/login',
		'/signup',
		'/onboarding',
		'/checkout',
		'/print-view'
	],
	
	// You can extend this for other layout features
	pagesWithoutNavigation: ['/login', '/signup'],
	fullScreenPages: ['/presentation', '/print-view']
};

export function shouldHideProfile(routeId: string| null) {

    if(routeId != null){
        return layoutConfig.pagesWithoutProfile.some(item => routeId.includes(item));
    }

    return false;
}